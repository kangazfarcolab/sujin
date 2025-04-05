.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: up
up: ## Start all services in development mode
	docker-compose -f docker-compose.dev.yml up -d

.PHONY: down
down: ## Stop all services
	docker-compose -f docker-compose.dev.yml down

.PHONY: logs
logs: ## Show logs from all services
	docker-compose -f docker-compose.dev.yml logs -f

.PHONY: build
build: ## Build all services
	docker-compose -f docker-compose.dev.yml build

.PHONY: restart
restart: down up ## Restart all services

.PHONY: backend-shell
backend-shell: ## Open a shell in the backend container
	docker-compose -f docker-compose.dev.yml exec backend /bin/bash

.PHONY: frontend-shell
frontend-shell: ## Open a shell in the frontend container
	docker-compose -f docker-compose.dev.yml exec frontend /bin/sh

.PHONY: db-shell
db-shell: ## Open a shell in the database container
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d fragent

.PHONY: migrate
migrate: ## Run database migrations
	docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

.PHONY: migration
migration: ## Create a new migration
	docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "$(message)"

.PHONY: test-backend
test-backend: ## Run backend tests
	docker-compose -f docker-compose.dev.yml exec backend pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	docker-compose -f docker-compose.dev.yml exec frontend npm test

.PHONY: lint-backend
lint-backend: ## Lint backend code
	docker-compose -f docker-compose.dev.yml exec backend ruff .
	docker-compose -f docker-compose.dev.yml exec backend black --check .
	docker-compose -f docker-compose.dev.yml exec backend mypy .

.PHONY: lint-frontend
lint-frontend: ## Lint frontend code
	docker-compose -f docker-compose.dev.yml exec frontend npm run lint

.PHONY: format-backend
format-backend: ## Format backend code
	docker-compose -f docker-compose.dev.yml exec backend black .
	docker-compose -f docker-compose.dev.yml exec backend isort .

.PHONY: clean
clean: ## Remove all containers, volumes, and images
	docker-compose -f docker-compose.dev.yml down -v --rmi all

.PHONY: prod-up
prod-up: ## Start all services in production mode
	docker-compose up -d

.PHONY: prod-down
prod-down: ## Stop all production services
	docker-compose down
