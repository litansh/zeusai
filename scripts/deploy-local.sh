#!/bin/bash

# ZeusAI Local Deployment Script
# This script deploys the complete ZeusAI platform locally

set -e

echo "🚀 ZeusAI Local Deployment"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the ZeusAI root directory"
    exit 1
fi

# Parse command line arguments
DEPLOY_TYPE="full"
SKIP_TESTS=false
SKIP_BUILD=false
FORCE_RECREATE=false
CLEAN_START=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            DEPLOY_TYPE="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --force-recreate)
            FORCE_RECREATE=true
            shift
            ;;
        --clean-start)
            CLEAN_START=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --type TYPE         Deployment type: full, minimal, production"
            echo "  --skip-tests        Skip running tests before deployment"
            echo "  --skip-build        Skip building Docker images"
            echo "  --force-recreate    Force recreate containers"
            echo "  --clean-start       Clean start (remove all containers and volumes)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "✓ All prerequisites are met"
}

# Function to run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Skipping tests as requested"
        return 0
    fi
    
    print_status "Running tests before deployment..."
    
    if [ -f "scripts/run-tests.sh" ]; then
        ./scripts/run-tests.sh --type unit --no-coverage
        if [ $? -ne 0 ]; then
            print_error "Tests failed. Deployment aborted."
            exit 1
        fi
        print_success "✓ Tests passed"
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Function to prepare environment
prepare_environment() {
    print_status "Preparing deployment environment..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/qdrant
    mkdir -p data/prometheus
    mkdir -p data/grafana
    mkdir -p data/loki
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual credentials"
    fi
    
    # Set proper permissions
    chmod 755 logs
    chmod 644 .env
    
    print_success "✓ Environment prepared"
}

# Function to clean start
clean_start() {
    if [ "$CLEAN_START" = true ]; then
        print_status "Performing clean start..."
        
        # Stop all containers
        docker-compose down --volumes --remove-orphans
        
        # Remove all images
        docker system prune -a --force
        
        # Remove all volumes
        docker volume prune --force
        
        print_success "✓ Clean start completed"
    fi
}

# Function to build images
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        print_warning "Skipping build as requested"
        return 0
    fi
    
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker-compose build zeusai-orchestrator
    
    # Build frontend image
    print_status "Building frontend image..."
    docker-compose build zeusai-ui
    
    # Build MCP services
    print_status "Building MCP services..."
    docker-compose build obs-mcp k8s-mcp git-mcp cloud-mcp kb-mcp deploy-mcp slo-mcp tf-migrator
    
    print_success "✓ All images built successfully"
}

# Function to deploy services
deploy_services() {
    print_status "Deploying ZeusAI services..."
    
    # Determine deployment command
    DEPLOY_CMD="docker-compose up -d"
    
    if [ "$FORCE_RECREATE" = true ]; then
        DEPLOY_CMD="docker-compose up -d --force-recreate"
    fi
    
    # Deploy based on type
    case $DEPLOY_TYPE in
        "minimal")
            print_status "Deploying minimal stack..."
            $DEPLOY_CMD postgres redis zeusai-orchestrator zeusai-ui
            ;;
        "production")
            print_status "Deploying production stack..."
            $DEPLOY_CMD
            ;;
        "full"|*)
            print_status "Deploying full stack..."
            $DEPLOY_CMD
            ;;
    esac
    
    print_success "✓ Services deployed successfully"
}

# Function to wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U zeusai; do sleep 2; done'
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for orchestrator
    print_status "Waiting for ZeusAI Orchestrator..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    
    # Wait for frontend
    print_status "Waiting for ZeusAI UI..."
    timeout 60 bash -c 'until curl -f http://localhost:3000; do sleep 2; done'
    
    print_success "✓ All services are ready"
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check orchestrator health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "✓ ZeusAI Orchestrator is healthy"
    else
        print_error "✗ ZeusAI Orchestrator health check failed"
        return 1
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "✓ ZeusAI UI is healthy"
    else
        print_error "✗ ZeusAI UI health check failed"
        return 1
    fi
    
    # Check database health
    if docker-compose exec -T postgres pg_isready -U zeusai > /dev/null 2>&1; then
        print_success "✓ PostgreSQL is healthy"
    else
        print_error "✗ PostgreSQL health check failed"
        return 1
    fi
    
    # Check Redis health
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "✓ Redis is healthy"
    else
        print_error "✗ Redis health check failed"
        return 1
    fi
    
    print_success "✓ All health checks passed"
}

# Function to show deployment info
show_deployment_info() {
    print_status "Deployment completed successfully!"
    echo ""
    echo "🌐 Access URLs:"
    echo "  • ZeusAI Dashboard: http://localhost:3000"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Grafana: http://localhost:3001 (admin/zeusai)"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo "🔑 Default Credentials:"
    echo "  • Username: admin"
    echo "  • Password: admin123"
    echo ""
    echo "📊 Monitoring:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Check status: docker-compose ps"
    echo "  • Stop services: docker-compose down"
    echo ""
    echo "🚀 Quick Start:"
    echo "  1. Open http://localhost:3000"
    echo "  2. Login with admin/admin123"
    echo "  3. Start designing infrastructure!"
    echo ""
}

# Function to handle errors
handle_error() {
    print_error "Deployment failed!"
    print_status "Cleaning up..."
    docker-compose down
    exit 1
}

# Set error handler
trap handle_error ERR

# Main deployment function
main() {
    print_status "Starting ZeusAI local deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Run tests
    run_tests
    
    # Prepare environment
    prepare_environment
    
    # Clean start if requested
    clean_start
    
    # Build images
    build_images
    
    # Deploy services
    deploy_services
    
    # Wait for services
    wait_for_services
    
    # Run health checks
    run_health_checks
    
    # Show deployment info
    show_deployment_info
}

# Run main function
main "$@"
