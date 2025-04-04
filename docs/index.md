# Sujin Documentation

Welcome to the Sujin Agent Framework documentation!

## Table of Contents

- [CLI Documentation](cli.md)
- [API Client Documentation](api_client.md)
- [MCP Architecture Documentation](mcp_architecture.md)

## Overview

Sujin (수진) is a comprehensive framework designed to simplify the development, deployment, and management of AI agents. It provides a structured approach to building agents that can perform a wide range of tasks, from simple automation to complex reasoning.

## Key Features

- **Modular Architecture**: Easily extend and customize agent capabilities
- **Pydantic Integration**: Strong typing and validation with Pydantic models
- **MCP Architecture**: Model-Controller-Plugin pattern for flexible, extensible agents
- **Plugin System**: Dynamically discover and load plugins
- **Tool Integration**: Seamlessly connect with external tools and APIs
- **Memory Management**: Sophisticated systems for short and long-term memory
- **Planning & Reasoning**: Advanced planning capabilities for complex tasks

## Getting Started

See the [README.md](../README.md) for installation instructions and basic usage examples.

## Components

### Core

- **Agent**: The main agent class that processes inputs and generates outputs
- **Models**: Pydantic models for data validation and serialization

### Plugins

- **Plugin System**: A flexible plugin architecture for extending agent capabilities
- **MCP Architecture**: Model-Controller-Plugin pattern for organizing code
  - **Model**: Data structures using Pydantic
  - **Controller**: Business logic for processing models
  - **Plugin**: Integration with the agent framework

### Tools

- **Tool**: Interface for defining tools that agents can use
- **Tool Schema**: Automatic schema generation for tools

### Memory

- **Memory**: Systems for storing and retrieving information

### Planning

- **Planner**: Systems for creating and executing plans

## Examples

Check out the `examples` directory for detailed examples of how to use the framework.
