"""
Console UI components for the Sujin CLI.
"""

import re
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.theme import Theme
from rich.table import Table
from rich import box

# Create a custom theme for Rich
CUSTOM_THEME = Theme({
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
console = Console(theme=CUSTOM_THEME)

# ASCII art banner
BANNER = """
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

def display_welcome(config: Dict[str, Any]) -> None:
    """
    Display welcome message and agent information.
    
    Args:
        config: Configuration dictionary
    """
    # Clear the screen
    console.clear()
    
    # Display the banner
    console.print(Panel(BANNER, border_style="agent"))
    
    # Create a table with agent information
    table = Table(box=box.ROUNDED, show_header=False, border_style="info")
    table.add_column("Property", style="bold")
    table.add_column("Value")
    
    table.add_row("Agent Name", f"[agent]{config['agent_name']}[/agent]")
    table.add_row("API Endpoint", f"[info]{config['api_url']}[/info]")
    table.add_row("Model", f"[highlight]{config['model']}[/highlight]")
    
    console.print(table)
    console.print("\n[system]Type 'exit' to quit. Type 'help' for available commands.[/system]\n")

def display_help() -> None:
    """Display help information."""
    help_table = Table(title="Available Commands", box=box.ROUNDED, border_style="info")
    help_table.add_column("Command", style="bold")
    help_table.add_column("Description")
    
    help_table.add_row("exit", "Exit the CLI")
    help_table.add_row("help", "Show this help message")
    help_table.add_row("clear", "Clear the screen")
    help_table.add_row("env", "Show current environment")
    
    console.print(help_table)

def display_env(config: Dict[str, Any]) -> None:
    """
    Display environment information.
    
    Args:
        config: Configuration dictionary
    """
    env_table = Table(title="Environment", box=box.ROUNDED, border_style="info")
    env_table.add_column("Setting", style="bold")
    env_table.add_column("Value")
    
    env_table.add_row("API URL", f"[info]{config['api_url']}[/info]")
    env_table.add_row("Model", f"[highlight]{config['model']}[/highlight]")
    env_table.add_row("Agent Name", f"[agent]{config['agent_name']}[/agent]")
    
    console.print(env_table)

def process_response(response_text: str) -> str:
    """
    Process the response text.
    
    Args:
        response_text: The raw response text
        
    Returns:
        The processed response text
    """
    import re
    
    # Keep the reasoning but mark it clearly
    reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response_text, flags=re.DOTALL)
    reasoning_content = ""
    if reasoning_match:
        reasoning_content = reasoning_match.group(1).strip()
        # Replace the tags with clear markers but keep the content
        cleaned_text = re.sub(r'<reasoning>(.*?)</reasoning>', r'\n\n--- REASONING ---\n\1\n--- END REASONING ---', response_text, flags=re.DOTALL)
    else:
        # If no reasoning tags, just use the response as is
        cleaned_text = response_text
    
    # Remove any <sep> tags and everything after them
    cleaned_text = re.sub(r'<sep>.*$', '', cleaned_text, flags=re.DOTALL)
    
    # If the response is empty after cleaning, provide a simple message
    if cleaned_text.strip() == "":
        cleaned_text = "I'm sorry, I couldn't generate a proper response."
    
    # Improve formatting for mathematical expressions
    # Replace LaTeX formatting with more readable symbols
    cleaned_text = re.sub(r'\\\(', '', cleaned_text)  # Remove \(
    cleaned_text = re.sub(r'\\\)', '', cleaned_text)  # Remove \)
    cleaned_text = re.sub(r'\\times', '×', cleaned_text)  # Replace \times with ×
    cleaned_text = re.sub(r'\\div', '÷', cleaned_text)  # Replace \div with ÷
    cleaned_text = re.sub(r'\\cdot', '·', cleaned_text)  # Replace \cdot with ·
    cleaned_text = re.sub(r'\\sqrt', '√', cleaned_text)  # Replace \sqrt with √
    cleaned_text = re.sub(r'\\pi', 'π', cleaned_text)  # Replace \pi with π
    cleaned_text = re.sub(r'\\boxed\{([^}]*)\}', r'\1', cleaned_text)  # Remove \boxed{}
    
    # Fix spacing around operators for better readability
    cleaned_text = re.sub(r'(\d)\s*([+\-×÷·])\s*(\d)', r'\1 \2 \3', cleaned_text)
    
    # Keep paragraph structure
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def display_response(response_text: str, response: Dict[str, Any]) -> None:
    """
    Display the response.
    
    Args:
        response_text: The processed response text
        response: The full API response
    """
    # Format the response
    # Simple text output without fancy formatting
    console.print("\n[agent]Response:[/agent]")
    console.print("-" * 80)
    console.print(response_text)
    console.print("-" * 80)
    
    # Print usage information if available
    if "usage" in response:
        usage = response["usage"]
        usage_table = Table(box=box.SIMPLE, show_header=False, title="Usage", title_style="metadata")
        usage_table.add_column("Metric", style="metadata")
        usage_table.add_column("Value", style="metadata")
        
        usage_table.add_row(
            "Tokens", 
            f"Total: {usage.get('total_tokens', 'N/A')} | "
            f"Prompt: {usage.get('prompt_tokens', 'N/A')} | "
            f"Completion: {usage.get('completion_tokens', 'N/A')}"
        )
        
        console.print(usage_table)
