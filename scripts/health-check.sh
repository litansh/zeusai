#!/bin/bash

# ZeusAI Health Check Script
# Comprehensive health monitoring for all ZeusAI services

set -e

echo "🏥 ZeusAI Health Check"
echo "====================="

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

# Health check results
HEALTH_STATUS=0
FAILED_CHECKS=()

# Function to check service health
check_service() {
    local service_name=$1
    local check_command=$2
    local timeout=${3:-30}
    
    print_status "Checking $service_name..."
    
    if timeout $timeout bash -c "$check_command" > /dev/null 2>&1; then
        print_success "✓ $service_name is healthy"
        return 0
    else
        print_error "✗ $service_name health check failed"
        FAILED_CHECKS+=("$service_name")
        HEALTH_STATUS=1
        return 1
    fi
}

# Function to check Docker service
check_docker_service() {
    local service_name=$1
    local health_endpoint=${2:-"/health"}
    local port=${3:-8000}
    
    print_status "Checking Docker service: $service_name..."
    
    # Check if container is running
    if ! docker-compose ps $service_name | grep -q "Up"; then
        print_error "✗ $service_name container is not running"
        FAILED_CHECKS+=("$service_name")
        HEALTH_STATUS=1
        return 1
    fi
    
    # Check health endpoint if specified
    if [ "$health_endpoint" != "/health" ]; then
        local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zeusai_${service_name}_1)
        if curl -f http://$container_ip:$port$health_endpoint > /dev/null 2>&1; then
            print_success "✓ $service_name is healthy"
            return 0
        else
            print_error "✗ $service_name health endpoint failed"
            FAILED_CHECKS+=("$service_name")
            HEALTH_STATUS=1
            return 1
        fi
    fi
    
    print_success "✓ $service_name is running"
    return 0
}

# Function to check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    # Check PostgreSQL
    if docker-compose exec -T postgres pg_isready -U zeusai > /dev/null 2>&1; then
        print_success "✓ PostgreSQL is healthy"
    else
        print_error "✗ PostgreSQL health check failed"
        FAILED_CHECKS+=("PostgreSQL")
        HEALTH_STATUS=1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "✓ Redis is healthy"
    else
        print_error "✗ Redis health check failed"
        FAILED_CHECKS+=("Redis")
        HEALTH_STATUS=1
    fi
    
    # Check Qdrant
    if curl -f http://localhost:6333/health > /dev/null 2>&1; then
        print_success "✓ Qdrant is healthy"
    else
        print_error "✗ Qdrant health check failed"
        FAILED_CHECKS+=("Qdrant")
        HEALTH_STATUS=1
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    print_status "Checking API endpoints..."
    
    # Check main orchestrator
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "✓ ZeusAI Orchestrator API is healthy"
    else
        print_error "✗ ZeusAI Orchestrator API health check failed"
        FAILED_CHECKS+=("ZeusAI Orchestrator API")
        HEALTH_STATUS=1
    fi
    
    # Check API documentation
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        print_success "✓ API Documentation is accessible"
    else
        print_error "✗ API Documentation is not accessible"
        FAILED_CHECKS+=("API Documentation")
        HEALTH_STATUS=1
    fi
    
    # Check MCP services
    local mcp_services=("obs-mcp" "k8s-mcp" "git-mcp" "cloud-mcp" "kb-mcp" "deploy-mcp" "slo-mcp" "tf-migrator")
    
    for service in "${mcp_services[@]}"; do
        local port=$(docker-compose port $service 8000 | cut -d: -f2)
        if [ ! -z "$port" ]; then
            if curl -f http://localhost:$port/health > /dev/null 2>&1; then
                print_success "✓ $service is healthy"
            else
                print_warning "⚠ $service health check failed"
                FAILED_CHECKS+=("$service")
            fi
        else
            print_warning "⚠ $service port not found"
        fi
    done
}

# Function to check frontend
check_frontend() {
    print_status "Checking frontend..."
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "✓ ZeusAI UI is accessible"
    else
        print_error "✗ ZeusAI UI is not accessible"
        FAILED_CHECKS+=("ZeusAI UI")
        HEALTH_STATUS=1
    fi
}

# Function to check monitoring stack
check_monitoring() {
    print_status "Checking monitoring stack..."
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        print_success "✓ Prometheus is healthy"
    else
        print_warning "⚠ Prometheus health check failed"
        FAILED_CHECKS+=("Prometheus")
    fi
    
    # Check Grafana
    if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
        print_success "✓ Grafana is healthy"
    else
        print_warning "⚠ Grafana health check failed"
        FAILED_CHECKS+=("Grafana")
    fi
    
    # Check Loki
    if curl -f http://localhost:3100/ready > /dev/null 2>&1; then
        print_success "✓ Loki is healthy"
    else
        print_warning "⚠ Loki health check failed"
        FAILED_CHECKS+=("Loki")
    fi
}

# Function to check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -lt 90 ]; then
        print_success "✓ Disk usage: ${disk_usage}%"
    else
        print_warning "⚠ Disk usage: ${disk_usage}% (high)"
        FAILED_CHECKS+=("High disk usage")
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ $memory_usage -lt 90 ]; then
        print_success "✓ Memory usage: ${memory_usage}%"
    else
        print_warning "⚠ Memory usage: ${memory_usage}% (high)"
        FAILED_CHECKS+=("High memory usage")
    fi
    
    # Check Docker resources
    local docker_disk_usage=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}" | grep Images | awk '{print $3}' | sed 's/[^0-9]//g')
    if [ $docker_disk_usage -lt 10000 ]; then
        print_success "✓ Docker disk usage: ${docker_disk_usage}MB"
    else
        print_warning "⚠ Docker disk usage: ${docker_disk_usage}MB (high)"
        FAILED_CHECKS+=("High Docker disk usage")
    fi
}

# Function to check network connectivity
check_network() {
    print_status "Checking network connectivity..."
    
    # Check localhost connectivity
    if ping -c 1 localhost > /dev/null 2>&1; then
        print_success "✓ Localhost connectivity"
    else
        print_error "✗ Localhost connectivity failed"
        FAILED_CHECKS+=("Localhost connectivity")
        HEALTH_STATUS=1
    fi
    
    # Check Docker network
    if docker network ls | grep -q zeusai_default; then
        print_success "✓ Docker network exists"
    else
        print_error "✗ Docker network not found"
        FAILED_CHECKS+=("Docker network")
        HEALTH_STATUS=1
    fi
}

# Function to check logs for errors
check_logs() {
    print_status "Checking recent logs for errors..."
    
    # Check for error logs in the last 10 minutes
    local error_count=$(docker-compose logs --since=10m 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    
    if [ $error_count -eq 0 ]; then
        print_success "✓ No recent errors found in logs"
    else
        print_warning "⚠ Found $error_count recent errors in logs"
        FAILED_CHECKS+=("Recent log errors")
    fi
}

# Function to generate health report
generate_health_report() {
    echo ""
    echo "📊 Health Check Summary"
    echo "======================"
    
    if [ $HEALTH_STATUS -eq 0 ]; then
        print_success "Overall Status: HEALTHY"
    else
        print_error "Overall Status: UNHEALTHY"
    fi
    
    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        echo ""
        echo "❌ Failed Checks:"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  • $check"
        done
    fi
    
    echo ""
    echo "🔧 Troubleshooting Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Restart services: docker-compose restart"
    echo "  • Check status: docker-compose ps"
    echo "  • Rebuild: docker-compose up --build -d"
    echo ""
}

# Main health check function
main() {
    print_status "Starting comprehensive health check..."
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the ZeusAI root directory"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "No ZeusAI services are running"
        echo "Start services with: docker-compose up -d"
        exit 1
    fi
    
    # Run all health checks
    check_network
    check_system_resources
    check_database
    check_api_endpoints
    check_frontend
    check_monitoring
    check_logs
    
    # Generate report
    generate_health_report
    
    # Exit with appropriate status
    exit $HEALTH_STATUS
}

# Run main function
main "$@"
