# Fra-Gent: AI Agent Framework

Fra-Gent is a comprehensive web-based framework for creating, managing, and orchestrating AI agents through an intuitive user interface.

![Fra-Gent Logo](docs/images/logo-placeholder.png)

## 🌟 Features

- **Agent Management**: Create, configure, and manage AI agents through a web UI
- **Workflow Builder**: Visual workflow editor to connect agents and tools
- **Knowledge Integration**: Provide agents with data and context
- **Execution Monitoring**: Track and monitor agent and workflow execution
- **Extensible Architecture**: Add custom tools and integrations

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/kangazfarcolab/fra-gent.git
cd fra-gent

# Start the application with Docker Compose
docker-compose up -d

# Access the web UI at http://localhost:3000
```

## 🏗️ Architecture

Fra-Gent follows a modern, modular architecture:

- **Backend**: FastAPI + PostgreSQL + LangChain
- **Frontend**: Next.js + React + TypeScript
- **Database**: PostgreSQL with vector extensions
- **Agent Framework**: LangChain with custom extensions

For more details, see [docs/architecture/README.md](docs/architecture/README.md).

## 🧩 Core Components

### Agent Management

Create and configure agents with different capabilities:

- Set agent parameters (model, temperature, etc.)
- Provide knowledge bases and context
- Monitor agent performance

### Workflow Builder

Connect agents and tools to create complex workflows:

- Visual drag-and-drop interface
- Data transformation between steps
- Conditional execution paths

### Execution Engine

Run and monitor agent and workflow execution:

- Real-time execution tracking
- Detailed logs and history
- Error handling and recovery

## 📊 Project Status

Fra-Gent is currently in active development. Check the [project board](https://github.com/kangazfarcolab/fra-gent/projects/1) for current status and roadmap.

### Current Focus

- Core agent management UI
- Basic workflow builder
- Agent execution engine

### Coming Soon

- Advanced workflow capabilities
- Tool/plugin system
- Knowledge base integration

## 🛠️ Development

For development setup and guidelines, see [docs/development/README.md](docs/development/README.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) for the agent framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- [Next.js](https://nextjs.org/) for the frontend framework
- [React Flow](https://reactflow.dev/) for the workflow editor
