# ZeusAI Makefile
# Comprehensive management commands for the ZeusAI platform

.PHONY: help install test deploy clean logs status stop start restart build lint format

# Default target
help:
	@echo "🚀 ZeusAI Platform Management"
	@echo "============================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install          Install all dependencies and setup environment"
	@echo "  setup            Quick setup (copy .env, create dirs)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-api         Run API tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-frontend    Run frontend tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  deploy           Deploy full stack locally"
	@echo "  deploy-minimal   Deploy minimal stack (core services only)"
	@echo "  deploy-prod      Deploy production configuration"
	@echo "  deploy-clean     Clean deployment (remove all containers/volumes)"
	@echo ""
	@echo "🔧 Development:"
	@echo "  build            Build all Docker images"
	@echo "  build-backend    Build backend image only"
	@echo "  build-frontend   Build frontend image only"
	@echo "  build-mcp        Build MCP services only"
	@echo ""
	@echo "📊 Monitoring & Management:"
	@echo "  start            Start all services"
	@echo "  stop             Stop all services"
	@echo "  restart          Restart all services"
	@echo "  status           Show service status"
	@echo "  logs             Show logs for all services"
	@echo "  logs-backend     Show backend logs"
	@echo "  logs-frontend    Show frontend logs"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            Clean up containers, images, and volumes"
	@echo "  clean-logs       Clean log files"
	@echo "  clean-data       Clean data volumes"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code"
	@echo "  security         Run security checks"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs             Generate documentation"
	@echo "  api-docs         Generate API documentation"
	@echo ""

# Setup & Installation
install: setup
	@echo "🔧 Installing dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "✅ Installation completed"

setup:
	@echo "🔧 Setting up ZeusAI environment..."
	@mkdir -p logs data/postgres data/redis data/qdrant data/prometheus data/grafana data/loki
	@if [ ! -f .env ]; then cp env.example .env; echo "📝 Created .env file from template"; fi
	@chmod 755 logs scripts/*.sh
	@chmod 644 .env
	@echo "✅ Setup completed"

# Testing
test:
	@echo "🧪 Running all tests..."
	@./scripts/run-tests.sh --type all

test-unit:
	@echo "🧪 Running unit tests..."
	@./scripts/run-tests.sh --type unit

test-api:
	@echo "🧪 Running API tests..."
	@./scripts/run-tests.sh --type api

test-integration:
	@echo "🧪 Running integration tests..."
	@./scripts/run-tests.sh --type integration

test-frontend:
	@echo "🧪 Running frontend tests..."
	@./scripts/run-tests.sh --type frontend

test-coverage:
	@echo "🧪 Running tests with coverage..."
	@./scripts/run-tests.sh --type all

# Deployment
deploy: test
	@echo "🚀 Deploying ZeusAI platform..."
	@./scripts/deploy-local.sh --type full

deploy-minimal: test
	@echo "🚀 Deploying minimal stack..."
	@./scripts/deploy-local.sh --type minimal

deploy-prod: test
	@echo "🚀 Deploying production configuration..."
	@./scripts/deploy-local.sh --type production

deploy-clean: clean
	@echo "🚀 Clean deployment..."
	@./scripts/deploy-local.sh --type full --clean-start

# Building
build:
	@echo "🔨 Building all Docker images..."
	@docker-compose build

build-backend:
	@echo "🔨 Building backend image..."
	@docker-compose build zeusai-orchestrator

build-frontend:
	@echo "🔨 Building frontend image..."
	@docker-compose build zeusai-ui

build-mcp:
	@echo "🔨 Building MCP services..."
	@docker-compose build obs-mcp k8s-mcp git-mcp cloud-mcp kb-mcp deploy-mcp slo-mcp tf-migrator

# Service Management
start:
	@echo "▶️  Starting ZeusAI services..."
	@docker-compose up -d

stop:
	@echo "⏹️  Stopping ZeusAI services..."
	@docker-compose down

restart: stop start
	@echo "🔄 Services restarted"

status:
	@echo "📊 ZeusAI Service Status:"
	@docker-compose ps

logs:
	@echo "📋 Showing logs for all services..."
	@docker-compose logs -f

logs-backend:
	@echo "📋 Showing backend logs..."
	@docker-compose logs -f zeusai-orchestrator

logs-frontend:
	@echo "📋 Showing frontend logs..."
	@docker-compose logs -f zeusai-ui

# Maintenance
clean:
	@echo "🧹 Cleaning up containers, images, and volumes..."
	@docker-compose down --volumes --remove-orphans
	@docker system prune -f
	@docker volume prune -f

clean-logs:
	@echo "🧹 Cleaning log files..."
	@rm -rf logs/*
	@mkdir -p logs

clean-data:
	@echo "🧹 Cleaning data volumes..."
	@docker-compose down --volumes
	@docker volume rm zeusai_postgres_data zeusai_redis_data zeusai_qdrant_data zeusai_prometheus_data zeusai_grafana_data zeusai_loki_data 2>/dev/null || true

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	@cd backend && python -m flake8 app/ --max-line-length=100 --ignore=E501,W503
	@cd frontend && npm run lint

format:
	@echo "🎨 Formatting code..."
	@cd backend && python -m black app/ --line-length=100
	@cd backend && python -m isort app/
	@cd frontend && npm run format

security:
	@echo "🔒 Running security checks..."
	@cd backend && python -m bandit -r app/ -f json -o security-report.json || true
	@cd frontend && npm audit

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@mkdir -p docs
	@echo "# ZeusAI Documentation" > docs/README.md
	@echo "Generated on $(date)" >> docs/README.md
	@echo "" >> docs/README.md
	@echo "## API Documentation" >> docs/README.md
	@echo "Visit http://localhost:8000/docs for interactive API documentation" >> docs/README.md

api-docs:
	@echo "📚 Generating API documentation..."
	@cd backend && python -c "import uvicorn; from app.main import app; import json; open('openapi.json', 'w').write(json.dumps(app.openapi(), indent=2))"

# Quick commands
quick-start: setup deploy
	@echo "🚀 ZeusAI is ready! Visit http://localhost:3000"

dev: setup
	@echo "🔧 Starting development environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

prod: setup
	@echo "🏭 Starting production environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health checks
health:
	@echo "🏥 Running health checks..."
	@curl -f http://localhost:8000/health || echo "❌ Backend health check failed"
	@curl -f http://localhost:3000 || echo "❌ Frontend health check failed"
	@docker-compose exec -T postgres pg_isready -U zeusai || echo "❌ Database health check failed"
	@docker-compose exec -T redis redis-cli ping || echo "❌ Redis health check failed"

# Backup and restore
backup:
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U zeusai zeusai > backups/zeusai_$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/"

restore:
	@echo "📥 Restoring from backup..."
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Please specify BACKUP_FILE=path/to/backup.sql"; exit 1; fi
	@docker-compose exec -T postgres psql -U zeusai -d zeusai < $(BACKUP_FILE)
	@echo "✅ Restore completed"

# Monitoring
monitor:
	@echo "📊 Opening monitoring dashboards..."
	@open http://localhost:3001  # Grafana
	@open http://localhost:9090  # Prometheus
	@open http://localhost:8000/docs  # API docs

# Development helpers
shell-backend:
	@echo "🐍 Opening backend shell..."
	@docker-compose exec zeusai-orchestrator /bin/bash

shell-frontend:
	@echo "🐍 Opening frontend shell..."
	@docker-compose exec zeusai-ui /bin/sh

# Database management
db-migrate:
	@echo "🗄️  Running database migrations..."
	@docker-compose exec zeusai-orchestrator alembic upgrade head

db-reset:
	@echo "🗄️  Resetting database..."
	@docker-compose exec -T postgres psql -U zeusai -d zeusai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@docker-compose exec zeusai-orchestrator alembic upgrade head

# Performance testing
perf-test:
	@echo "⚡ Running performance tests..."
	@cd backend && python -m pytest tests/test_performance.py -v

# Load testing
load-test:
	@echo "📈 Running load tests..."
	@docker run --rm -v $(PWD)/tests:/tests -w /tests k6sio/k6 run load-test.js

# Show system info
info:
	@echo "ℹ️  ZeusAI System Information:"
	@echo "Version: 1.0.0"
	@echo "Environment: $(shell grep ENVIRONMENT .env | cut -d'=' -f2 || echo 'development')"
	@echo "Docker Compose: $(shell docker-compose --version)"
	@echo "Python: $(shell python3 --version)"
	@echo "Node: $(shell node --version)"
	@echo "Docker: $(shell docker --version)"
