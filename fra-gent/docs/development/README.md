# Development Guide

This document provides guidelines and instructions for developing the Fra-Gent AI Agent Framework.

## Development Environment Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Docker and Docker Compose**
- **PostgreSQL 14+** (or use the Docker Compose setup)
- **Git**

### Local Setup

1. **Clone the repository**

```bash
git clone https://github.com/kangazfarcolab/fra-gent.git
cd fra-gent
```

2. **Backend setup**

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with Poetry
pip install poetry
poetry install

# Set up pre-commit hooks
pre-commit install

# Create a .env file
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend setup**

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Database setup**

```bash
# Using Docker Compose
docker-compose up -d postgres

# Or manually
# 1. Create a PostgreSQL database
# 2. Update the DATABASE_URL in .env
# 3. Run migrations
alembic upgrade head
```

5. **Start the development servers**

```bash
# Backend (from the project root)
uvicorn backend.main:app --reload

# Frontend (from the frontend directory)
npm run dev
```

## Docker Development Environment

For a fully containerized development environment:

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

## Project Structure

```
fra-gent/
├── backend/                 # Backend code
│   ├── alembic/             # Database migrations
│   ├── app/                 # Application code
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database models and utilities
│   │   ├── agents/          # Agent framework
│   │   ├── workflows/       # Workflow engine
│   │   └── utils/           # Utility functions
│   ├── tests/               # Backend tests
│   └── main.py              # Application entry point
├── frontend/                # Frontend code
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── lib/                 # Utility functions
│   ├── public/              # Static files
│   └── styles/              # CSS styles
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── .github/                 # GitHub workflows and templates
├── docker/                  # Docker configuration
├── docker-compose.yml       # Production Docker Compose
├── docker-compose.dev.yml   # Development Docker Compose
├── .env.example             # Example environment variables
└── README.md                # Project README
```

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints
- Write docstrings for all functions, classes, and modules
- Use f-strings for string formatting
- Use pathlib for file path manipulation

### TypeScript/JavaScript

- Follow the ESLint and Prettier configuration
- Use TypeScript for all new code
- Use functional components with hooks for React
- Use named exports instead of default exports
- Use async/await instead of promises

### Git

- Use feature branches for all changes
- Write descriptive commit messages
- Reference issue numbers in commit messages
- Keep commits focused on a single change
- Rebase feature branches on main before merging

## Testing

### Backend Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=backend

# Run specific tests
pytest backend/tests/test_agents.py
```

### Frontend Testing

```bash
# Run all tests
cd frontend
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific tests
npm test -- components/AgentCard
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Documentation

The API documentation is available at `/docs` when running the backend server.

## Troubleshooting

### Common Issues

1. **Database connection issues**
   - Check that PostgreSQL is running
   - Verify the DATABASE_URL in .env
   - Ensure the database exists

2. **Frontend build issues**
   - Clear the Next.js cache: `rm -rf frontend/.next`
   - Reinstall dependencies: `cd frontend && rm -rf node_modules && npm install`

3. **Docker issues**
   - Check Docker logs: `docker-compose logs -f`
   - Rebuild containers: `docker-compose build --no-cache`

## Deployment

### Production Deployment

```bash
# Build and start production containers
docker-compose up -d

# Apply database migrations
docker-compose exec backend alembic upgrade head
```

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

- **CI**: Runs on all pull requests to main
  - Linting
  - Testing
  - Building

- **CD**: Runs on pushes to main
  - Building
  - Deploying to staging
  - Deploying to production (manual approval)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
