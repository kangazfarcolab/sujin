#!/usr/bin/env python
"""
Command-line interface for the Sujin Agent Framework.
"""

import os
import sys
import argparse
import logging
import time
from typing import Dict, List, Optional, Any

# Rich library for better CLI formatting
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich.table import Table
from rich import box

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.sujin.core.agent import Agent
from src.sujin.core.models import Message, AgentInput, AgentOutput, ToolCall
from src.sujin.tools.base import Tool
from src.sujin.clients.custom_api import CustomAPIClient
from src.sujin.plugins.mcp.example import ExampleMCPPlugin


class CliAgent(Agent):
    """Agent for CLI interactions."""

    def __init__(
        self,
        name: str = "CliAgent",
        description: str = "CLI Agent for Sujin framework",
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_mcp: bool = False,
        verbose: bool = False
    ):
        """
        Initialize a new CLI Agent.

        Args:
            name: The name of the agent
            description: A description of the agent's purpose
            api_url: URL for the custom API (if None, no API client is created)
            api_key: API key for the custom API
            model: Model to use with the API
            use_mcp: Whether to use the MCP architecture
            verbose: Whether to enable verbose logging
        """
        super().__init__(name, description)

        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create API client if URL and key are provided
        self.api_client = None
        if api_url and api_key:
            # Disable SSL verification if using IP address
            import re
            hostname = re.search(r'https?://([^:/]+)', api_url)
            verify_ssl = not (hostname and re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname.group(1)))

            self.api_client = CustomAPIClient(
                base_url=api_url,
                api_key=api_key,
                default_model=model or "gpt-3.5-turbo",
                verify_ssl=verify_ssl
            )

            if not verify_ssl:
                logging.warning("SSL verification disabled for IP address")

            logging.info(f"Created API client for {api_url} with model {model or 'gpt-3.5-turbo'}")

        # Add tools
        self.add_tool(Tool(
            name="echo",
            description="Echo a message back",
            func=self.echo
        ))

        # Register MCP plugin if requested
        if use_mcp:
            self.register_plugin(ExampleMCPPlugin())
            logging.info("Registered ExampleMCPPlugin")

    def echo(self, message: str) -> str:
        """Echo a message back.

        Args:
            message: The message to echo

        Returns:
            The same message
        """
        return message

    def run(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return a response.

        Args:
            input_data: The input data to process

        Returns:
            The agent's output
        """
        # Get the last user message
        last_message = input_data.messages[-1] if input_data.messages else None
        if not last_message or last_message.role != "user":
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content="I didn't receive a user message."
                )
            )

        content = last_message.content

        # If we have an API client, use it
        if self.api_client:
            try:
                # Prepare messages for the API
                messages = []
                for msg in input_data.messages:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

                # Add a system message if none exists
                if not any(msg["role"] == "system" for msg in messages):
                    messages.insert(0, {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    })

                # Call the API
                logging.debug(f"Calling API with messages: {messages}")
                response = self.api_client.chat_completion(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150,
                    timeout=30
                )

                # Extract the response
                if response and "choices" in response and len(response["choices"]) > 0:
                    choice = response["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        api_content = choice["message"]["content"]

                        # Create metadata with usage information
                        metadata = {}
                        if "usage" in response:
                            metadata["usage"] = response["usage"]

                        return AgentOutput(
                            message=Message(
                                role="assistant",
                                content=api_content,
                                metadata=metadata
                            )
                        )
            except Exception as e:
                logging.error(f"Error calling API: {e}")
                return AgentOutput(
                    message=Message(
                        role="assistant",
                        content=f"I encountered an error when calling the API: {str(e)}"
                    )
                )

        # If we don't have an API client or the API call failed, use a built-in response system
        if content.startswith("echo "):
            message = content[5:]
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content=self.echo(message)
                ),
                tool_calls=[
                    ToolCall(
                        tool_name="echo",
                        parameters={"message": message}
                    )
                ]
            )
        else:
            # Simple built-in responses for common questions
            response = self.get_built_in_response(content)
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content=response
                )
            )

    def get_built_in_response(self, query: str) -> str:
        """Get a built-in response for common questions.

        Args:
            query: The user's query

        Returns:
            A response to the query
        """
        # Convert to lowercase for easier matching
        query_lower = query.lower()

        # Greetings
        if any(greeting in query_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return f"Hello! I'm {self.name}, a simple CLI agent. How can I help you today?"

        # Questions about capabilities
        elif any(word in query_lower for word in ["what can you do", "help me", "capabilities", "functions"]):
            return (
                f"I'm {self.name}, a simple CLI agent. Without an API connection, my capabilities are limited, but I can:\n\n"
                "1. Respond to basic questions\n"
                "2. Echo messages back to you (try 'echo [message]')\n"
                "3. Provide information about the Sujin framework\n\n"
                "For more advanced capabilities, please connect me to an API using the --api-url and --api-key parameters."
            )

        # Questions about the agent
        elif any(word in query_lower for word in ["who are you", "what are you", "your name"]):
            return f"I'm {self.name}, an AI assistant powered by the Sujin Agent Framework. I'm currently running in CLI mode."

        # Questions about Sujin
        elif "sujin" in query_lower:
            return (
                "Sujin (수진) is a comprehensive framework designed to simplify the development, deployment, "
                "and management of AI agents. It provides a structured approach to building agents that can "
                "perform a wide range of tasks, from simple automation to complex reasoning.\n\n"
                "The framework includes:\n"
                "- Modular Architecture: Easily extend and customize agent capabilities\n"
                "- Pydantic Integration: Strong typing and validation with Pydantic models\n"
                "- MCP Architecture: Model-Controller-Plugin pattern for flexible, extensible agents\n"
                "- Plugin System: Dynamically discover and load plugins\n"
                "- Tool Integration: Seamlessly connect with external tools and APIs"
            )

        # Math questions
        elif any(op in query_lower for op in ["+", "plus", "add", "-", "minus", "subtract", "*", "multiply", "/", "divide"]):
            return "I can perform basic math operations when connected to an API. Please connect me to an API for this functionality."

        # Default response
        else:
            return (
                f"I'm a simple CLI agent without an API connection, so my responses are limited. "
                f"Try 'echo [message]' to use my echo tool, or ask me about my capabilities or about the Sujin framework.\n\n"
                f"For more advanced functionality, please run me with an API connection using:\n"
                f"python sujin_cli.py --api-url \"https://your-api-url\" --api-key \"your-api-key\" --model \"your-model\""
            )


def main():
    """Main entry point for the CLI."""
    # Create a custom theme for Rich
    custom_theme = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "green",
        "agent": "bold blue",
        "user": "bold white",
        "system": "italic yellow",
        "metadata": "dim cyan",
        "highlight": "magenta",
    })

    # Create a console with the custom theme
    console = Console(theme=custom_theme)

    parser = argparse.ArgumentParser(description="Sujin Agent Framework CLI")

    # Basic configuration
    parser.add_argument("--name", default="Sujin", help="Name of the agent")
    parser.add_argument("--description", default="AI Assistant powered by Sujin Agent Framework", help="Description of the agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # API configuration
    parser.add_argument("--api-url", default=os.environ.get("CUSTOM_API_URL"), help="URL for the custom API")
    parser.add_argument("--api-ip", default=None, help="IP address to use instead of hostname resolution")
    parser.add_argument("--api-key", default=os.environ.get("CUSTOM_API_KEY"), help="API key for the custom API")
    parser.add_argument("--model", default=os.environ.get("CUSTOM_API_MODEL"), help="Model to use with the API")

    # Feature flags
    parser.add_argument("--use-mcp", action="store_true", help="Use the MCP architecture")
    parser.add_argument("--theme", default="dark", choices=["dark", "light"], help="Color theme for the CLI")

    # Parse arguments
    args = parser.parse_args()

    # Modify API URL if IP is provided
    api_url = args.api_url
    if args.api_ip and args.api_url:
        # Extract hostname from URL
        import urllib.parse
        parsed_url = urllib.parse.urlparse(args.api_url)
        hostname = parsed_url.netloc

        # Replace hostname with IP in the URL
        if ':' in hostname:  # If there's a port
            host, port = hostname.split(':')
            new_hostname = f"{args.api_ip}:{port}"
        else:
            new_hostname = args.api_ip

        # Reconstruct URL with IP
        api_url = args.api_url.replace(hostname, new_hostname)

        # Add Host header to requests
        os.environ['CUSTOM_HOST_HEADER'] = hostname

        console.print(f"[info]Using IP address {args.api_ip} instead of {hostname}[/info]")
        console.print(f"[info]Modified URL: {api_url}[/info]")

    # Clear the screen
    console.clear()

    # Display a welcome banner
    banner = """
    ╭───────────────────────────────────────────────╮
    │                                               │
    │   ███████╗██╗   ██╗     ██╗██╗███╗   ██╗     │
    │   ██╔════╝██║   ██║     ██║██║████╗  ██║     │
    │   ███████╗██║   ██║     ██║██║██╔██╗ ██║     │
    │   ╚════██║██║   ██║██   ██║██║██║╚██╗██║     │
    │   ███████║╚██████╔╝╚█████╔╝██║██║ ╚████║     │
    │   ╚══════╝ ╚═════╝  ╚════╝ ╚═╝╚═╝  ╚═══╝     │
    │                                               │
    │           Agent Framework CLI                 │
    │                                               │
    ╰───────────────────────────────────────────────╯
    """
    console.print(Panel(banner, border_style="agent"))

    # Create the agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[info]Initializing agent...[/info]"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task("init", total=None)
        agent = CliAgent(
            name=args.name,
            description=args.description,
            api_url=api_url,
            api_key=args.api_key,
            model=args.model,
            use_mcp=args.use_mcp,
            verbose=args.verbose
        )

    # Create a table with agent information
    table = Table(box=box.ROUNDED, show_header=False, border_style="info")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Agent Name", f"[agent]{agent.name}[/agent]")
    table.add_row("Description", agent.description)
    if agent.api_client:
        table.add_row("API Endpoint", f"[info]{args.api_url}[/info]")
        table.add_row("Model", f"[highlight]{args.model or 'default'}[/highlight]")
    if args.use_mcp:
        table.add_row("MCP Architecture", "[success]Enabled[/success]")

    console.print(table)
    console.print("\n[system]Type 'exit' to quit. Type 'help' for available commands.[/system]\n")

    # Command history and system message
    command_history = []
    system_message = "You are a helpful assistant."

    # Help command
    def show_help():
        help_table = Table(title="Available Commands", box=box.ROUNDED, border_style="info")
        help_table.add_column("Command", style="bold")
        help_table.add_column("Description")

        help_table.add_row("exit", "Exit the CLI")
        help_table.add_row("help", "Show this help message")
        help_table.add_row("clear", "Clear the screen")
        help_table.add_row("history", "Show command history")
        help_table.add_row("info", "Show agent information")
        help_table.add_row("echo [text]", "Echo text back using the echo tool")
        help_table.add_row("model [name]", "Change the model (if API is enabled)")
        help_table.add_row("system [text]", "Set a custom system message")

        console.print(help_table)

    # Enhanced REPL
    while True:
        try:
            # Use Rich's Prompt for better input
            user_input = Prompt.ask("\n[bold white]>[/bold white]", console=console)

            # Access the system message (defined above)

            # Process special commands
            if user_input.lower() == "exit":
                console.print("\n[system]Exiting...[/system]")
                break
            elif user_input.lower() == "help":
                show_help()
                continue
            elif user_input.lower() == "clear":
                console.clear()
                continue
            elif user_input.lower() == "history":
                if command_history:
                    history_table = Table(title="Command History", box=box.SIMPLE)
                    history_table.add_column("#", style="dim")
                    history_table.add_column("Command")

                    for i, cmd in enumerate(command_history, 1):
                        history_table.add_row(str(i), cmd)

                    console.print(history_table)
                else:
                    console.print("[warning]No command history yet.[/warning]")
                continue
            elif user_input.lower() == "info":
                # Show agent information
                table = Table(box=box.ROUNDED, show_header=False, border_style="info")
                table.add_column("Property", style="bold")
                table.add_column("Value")

                table.add_row("Agent Name", f"[agent]{agent.name}[/agent]")
                table.add_row("Description", agent.description)
                if agent.api_client:
                    table.add_row("API Endpoint", f"[info]{args.api_url}[/info]")
                    table.add_row("Model", f"[highlight]{args.model or 'default'}[/highlight]")
                if args.use_mcp:
                    table.add_row("MCP Architecture", "[success]Enabled[/success]")

                console.print(table)
                continue
            elif user_input.lower().startswith("echo "):
                # Echo command
                echo_text = user_input[5:]
                console.print(Panel(echo_text, title="[agent]Echo[/agent]", border_style="agent"))
                continue
            elif user_input.lower().startswith("model ") and agent.api_client:
                # Change model
                new_model = user_input[6:].strip()
                if new_model:
                    old_model = agent.api_client.default_model
                    agent.api_client.default_model = new_model
                    console.print(f"[success]Model changed from [highlight]{old_model}[/highlight] to [highlight]{new_model}[/highlight][/success]")
                else:
                    console.print(f"[warning]Current model: [highlight]{agent.api_client.default_model}[/highlight][/warning]")
                continue
            elif user_input.lower().startswith("system "):
                # Set system message
                system_message = user_input[7:].strip()
                if system_message:
                    console.print(f"[success]System message set to: [system]{system_message}[/system][/success]")
                else:
                    system_message = "You are a helpful assistant."
                    console.print(f"[warning]System message reset to default: [system]{system_message}[/system][/warning]")
                continue

            # Add to command history if not empty
            if user_input.strip() and user_input.lower() not in ["exit", "help", "clear", "history", "info"]:
                command_history.append(user_input)

            # Show user message
            console.print(f"\n[user]{user_input}[/user]")

            # Process the input with a spinner
            with Progress(
                SpinnerColumn(),
                TextColumn("[info]Thinking...[/info]"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("thinking", total=None)

                # Create input with system message
                agent_input = AgentInput(
                    messages=[
                        Message(role="system", content=system_message),
                        Message(role="user", content=user_input)
                    ],
                    tools=agent.get_tool_schemas()
                )

                # Process the input
                output = agent.process(agent_input)

            # Print the response in a panel
            response_md = Markdown(output.message.content)
            console.print(Panel(response_md, title="[agent]Response[/agent]", border_style="agent", expand=False))

            # Print metadata if available
            if output.message.metadata:
                metadata_table = Table(box=box.SIMPLE, show_header=False, title="Metadata", title_style="metadata")
                metadata_table.add_column("Key", style="metadata")
                metadata_table.add_column("Value", style="metadata")

                for key, value in output.message.metadata.items():
                    if key == "usage":
                        metadata_table.add_row(
                            "Tokens",
                            f"Total: {value.get('total_tokens', 'N/A')} | "
                            f"Prompt: {value.get('prompt_tokens', 'N/A')} | "
                            f"Completion: {value.get('completion_tokens', 'N/A')}"
                        )
                    else:
                        metadata_table.add_row(key, str(value))

                console.print(metadata_table)

        except KeyboardInterrupt:
            console.print("\n[system]Exiting...[/system]")
            break
        except Exception as e:
            console.print(f"\n[error]Error: {e}[/error]")


if __name__ == "__main__":
    main()
