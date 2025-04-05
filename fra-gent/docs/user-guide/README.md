# Fra-Gent User Guide

Welcome to the Fra-Gent AI Agent Framework! This guide will help you get started with creating, managing, and orchestrating AI agents through the Fra-Gent web interface.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Agents](#creating-agents)
3. [Building Workflows](#building-workflows)
4. [Executing Workflows](#executing-workflows)
5. [Managing Knowledge](#managing-knowledge)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Web Interface

After installing Fra-Gent, you can access the web interface at `http://localhost:3000` (or the configured URL if different).

### Dashboard Overview

The dashboard provides an overview of your agents, workflows, and recent executions. From here, you can:

- View all agents
- View all workflows
- See recent executions
- Access system settings

### Navigation

The main navigation menu includes:

- **Dashboard**: Overview of the system
- **Agents**: Create and manage agents
- **Workflows**: Create and manage workflows
- **Knowledge**: Manage knowledge bases
- **Executions**: View execution history
- **Settings**: Configure system settings

## Creating Agents

### What is an Agent?

An agent is an AI assistant configured for a specific purpose. Agents can:

- Answer questions
- Perform tasks
- Process data
- Interact with other agents and tools

### Creating a New Agent

To create a new agent:

1. Go to the **Agents** page
2. Click **Create Agent**
3. Fill in the agent details:
   - **Name**: A descriptive name for the agent
   - **Description**: What the agent does
   - **Model**: The AI model to use (e.g., GPT-4, Claude)
   - **System Prompt**: Instructions for the agent
   - **Temperature**: Controls randomness (0.0-1.0)
   - **Max Tokens**: Maximum response length

4. Click **Create** to save the agent

### Agent Configuration Options

#### Basic Configuration

- **Name**: Identifies the agent in the system
- **Description**: Helps you remember the agent's purpose
- **Model**: Determines the AI capabilities

#### Advanced Configuration

- **System Prompt**: Defines the agent's behavior and capabilities
- **Temperature**: Higher values make output more random, lower values more deterministic
- **Max Tokens**: Limits the length of responses
- **Top P**: Controls diversity via nucleus sampling
- **Frequency Penalty**: Reduces repetition of tokens
- **Presence Penalty**: Reduces repetition of topics

### Testing Agents

To test an agent:

1. Go to the agent details page
2. Use the **Test** panel to send messages
3. View the agent's responses
4. Adjust configuration as needed

## Building Workflows

### What is a Workflow?

A workflow connects multiple agents and tools to perform complex tasks. Workflows consist of:

- **Nodes**: Agents, tools, and data processors
- **Connections**: Data flow between nodes
- **Inputs**: Starting points for the workflow
- **Outputs**: Results of the workflow

### Creating a New Workflow

To create a new workflow:

1. Go to the **Workflows** page
2. Click **Create Workflow**
3. Fill in the workflow details:
   - **Name**: A descriptive name
   - **Description**: What the workflow does
4. Click **Create** to open the workflow editor

### Using the Workflow Editor

The workflow editor provides a canvas where you can:

1. **Add nodes**: Drag agents and tools from the sidebar
2. **Connect nodes**: Click and drag from one node's output to another node's input
3. **Configure nodes**: Click on a node to edit its settings
4. **Test connections**: Verify data flow between nodes
5. **Save the workflow**: Click **Save** to store your changes

### Node Types

- **Agent Nodes**: AI agents that process information
- **Input Nodes**: Entry points for data
- **Output Nodes**: Exit points for results
- **Transformation Nodes**: Process and transform data
- **Conditional Nodes**: Branch based on conditions
- **Loop Nodes**: Repeat operations

### Connection Types

- **Data Connections**: Pass data between nodes
- **Control Connections**: Determine execution flow
- **Context Connections**: Share context between nodes

## Executing Workflows

### Starting a Workflow

To execute a workflow:

1. Go to the workflow details page
2. Click **Execute**
3. Provide any required inputs
4. Click **Start** to begin execution

### Monitoring Execution

During execution, you can:

- View the current status of each node
- See data flowing through connections
- Monitor execution logs
- Pause or stop execution if needed

### Viewing Results

After execution completes:

1. View the execution summary
2. Examine outputs from each node
3. Download results if needed
4. View execution logs for debugging

### Scheduling Workflows

To schedule a workflow:

1. Go to the workflow details page
2. Click **Schedule**
3. Set the schedule parameters:
   - One-time execution
   - Recurring execution (hourly, daily, weekly)
   - Trigger-based execution
4. Click **Save Schedule**

## Managing Knowledge

### Knowledge Bases

Knowledge bases provide information to agents. Types include:

- **Document Collections**: PDFs, Word documents, etc.
- **Structured Data**: CSV, JSON, databases
- **Web Content**: Websites, APIs
- **Custom Knowledge**: Manually entered information

### Creating a Knowledge Base

To create a knowledge base:

1. Go to the **Knowledge** page
2. Click **Create Knowledge Base**
3. Fill in the details:
   - **Name**: A descriptive name
   - **Description**: What information it contains
   - **Type**: Document, structured, web, or custom
4. Upload or connect to the data source
5. Click **Create** to process and index the knowledge

### Using Knowledge with Agents

To connect a knowledge base to an agent:

1. Go to the agent details page
2. Click **Edit**
3. In the **Knowledge** section, select the knowledge base
4. Configure retrieval settings:
   - **Retrieval Method**: How information is retrieved
   - **Relevance Threshold**: Minimum relevance score
   - **Max Chunks**: Maximum pieces of information to retrieve
5. Click **Save** to update the agent

## Troubleshooting

### Common Issues

#### Agent Issues

- **Agent not responding**: Check model availability and API keys
- **Poor responses**: Adjust system prompt and temperature
- **Token limits**: Increase max tokens or optimize prompts

#### Workflow Issues

- **Workflow stuck**: Check for missing inputs or configuration
- **Connection errors**: Verify data compatibility between nodes
- **Performance issues**: Optimize node configuration and data flow

#### Knowledge Base Issues

- **Indexing failures**: Check file formats and permissions
- **Retrieval problems**: Adjust relevance settings
- **Missing information**: Update knowledge base with new data

### Getting Help

- Check the [documentation](https://github.com/kangazfarcolab/fra-gent/docs)
- Search [GitHub issues](https://github.com/kangazfarcolab/fra-gent/issues)
- Join the [community forum](https://github.com/kangazfarcolab/fra-gent/discussions)
- Contact support at support@fra-gent.com
