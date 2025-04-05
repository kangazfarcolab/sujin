# Sujin CLI Documentation

The Sujin Command Line Interface (CLI) provides a simple way to interact with the Sujin Agent Framework.

## Installation

Before using the CLI, make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

The CLI requires certain environment variables to be set. You can set these up using the environment setup wizard:

```bash
python sujin.py env
```

This wizard will guide you through setting up:

1. **API Configuration**:
   - **Host URL**: The URL of the API endpoint (e.g., `https://llm.chutes.ai/v1/chat/completions`)
   - **API Key**: Your API key for authentication
   - **Model**: The model to use for generating responses

2. **Agent Configuration**:
   - **Agent Name**: The name of your agent
   - **Agent Description**: A description of your agent

The wizard will create a `.env` file with these settings.

## Running the CLI

To start the CLI:

```bash
python sujin.py
```

This will load the environment variables from the `.env` file and start the CLI.

## CLI Commands

Once the CLI is running, you can use the following commands:

### Basic Commands

- `help`: Show a list of available commands
- `exit`: Exit the CLI
- `clear`: Clear the screen
- `env`: Show the current environment settings

### Interacting with the Agent

Simply type your message and press Enter to send it to the agent. The agent will process your message and respond.

Example:

```
> Hello, how are you?
Thinking...

Response:
--------------------------------------------------------------------------------
I'm doing well, thank you for asking! How can I assist you today?
--------------------------------------------------------------------------------
```

## Command Line Arguments

The CLI supports the following command line arguments:

- `env`: Run the environment setup wizard
  ```bash
  python sujin.py env
  ```

- `run`: Run the CLI (default if no command is specified)
  ```bash
  python sujin.py run
  ```

- `--verbose`: Enable verbose logging
  ```bash
  python sujin.py --verbose
  ```

## Customizing the CLI

You can customize the CLI by modifying the `sujin.py` file. Some possible customizations include:

- Adding new commands
- Changing the appearance of the CLI
- Adding support for additional API endpoints
- Implementing new features

## Troubleshooting

### Missing Environment Variables

If you see an error about missing environment variables, run the environment setup wizard:

```bash
python sujin.py env
```

### API Connection Issues

If you're having trouble connecting to the API:

1. Check that your API URL is correct
2. Verify that your API key is valid
3. Ensure that the API endpoint is accessible from your network
4. Check for any firewall or proxy settings that might be blocking the connection

### Other Issues

For other issues, check the logs for more information. You can enable verbose logging with the `--verbose` flag:

```bash
python sujin.py --verbose
```
