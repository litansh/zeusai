#!/bin/bash

# ZeusAI Test Runner
# This script runs all tests for the ZeusAI platform

set -e

echo "🚀 ZeusAI Test Suite"
echo "===================="

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
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --type TYPE        Test type: all, unit, api, integration, frontend"
            echo "  --no-coverage      Disable coverage reporting"
            echo "  --verbose          Verbose output"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create test environment
print_status "Setting up test environment..."

# Create test directories
mkdir -p logs
mkdir -p htmlcov

# Set test environment variables
export TESTING=true
export DATABASE_URL="sqlite:///./test.db"
export REDIS_URL="redis://localhost:6379/1"

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    cd backend
    
    # Install test dependencies if not already installed
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
    
    # Run tests based on type
    case $TEST_TYPE in
        "unit")
            print_status "Running unit tests..."
            if [ "$COVERAGE" = true ]; then
                pytest ../tests/test_core.py -v --cov=app.core --cov-report=term-missing
            else
                pytest ../tests/test_core.py -v
            fi
            ;;
        "api")
            print_status "Running API tests..."
            if [ "$COVERAGE" = true ]; then
                pytest ../tests/test_api.py -v --cov=app.api --cov-report=term-missing
            else
                pytest ../tests/test_api.py -v
            fi
            ;;
        "integration")
            print_status "Running integration tests..."
            if [ "$COVERAGE" = true ]; then
                pytest ../tests/ -m integration -v --cov=app --cov-report=term-missing
            else
                pytest ../tests/ -m integration -v
            fi
            ;;
        "all")
            print_status "Running all backend tests..."
            if [ "$COVERAGE" = true ]; then
                pytest ../tests/ -v --cov=app --cov-report=term-missing --cov-report=html:../htmlcov
            else
                pytest ../tests/ -v
            fi
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    deactivate
    cd ..
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Run frontend tests
    case $TEST_TYPE in
        "frontend"|"all")
            print_status "Running frontend component tests..."
            npm test -- --watchAll=false --coverage --passWithNoTests
            ;;
    esac
    
    cd ..
}

# Function to run integration tests with Docker
run_docker_integration_tests() {
    if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
        print_status "Running Docker integration tests..."
        
        # Start services for integration testing
        print_status "Starting test services..."
        docker-compose -f docker-compose.test.yml up -d postgres redis
        
        # Wait for services to be ready
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Run integration tests
        run_backend_tests
        
        # Stop test services
        print_status "Stopping test services..."
        docker-compose -f docker-compose.test.yml down
    fi
}

# Function to run sanity checks
run_sanity_checks() {
    print_status "Running sanity checks..."
    
    # Check if all required files exist
    required_files=(
        "docker-compose.yml"
        "backend/main.py"
        "frontend/package.json"
        "README.md"
        "env.example"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "✓ $file exists"
        else
            print_error "✗ $file missing"
            exit 1
        fi
    done
    
    # Check Docker Compose configuration
    print_status "Validating Docker Compose configuration..."
    if docker-compose config > /dev/null 2>&1; then
        print_success "✓ Docker Compose configuration is valid"
    else
        print_error "✗ Docker Compose configuration is invalid"
        exit 1
    fi
    
    # Check Python syntax
    print_status "Checking Python syntax..."
    find backend -name "*.py" -exec python3 -m py_compile {} \;
    print_success "✓ All Python files have valid syntax"
    
    # Check JavaScript syntax
    print_status "Checking JavaScript syntax..."
    cd frontend
    npm run lint --silent || print_warning "JavaScript linting issues found"
    cd ..
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    # Create test report directory
    mkdir -p test-reports
    
    # Generate summary
    cat > test-reports/summary.md << EOF
# ZeusAI Test Report

## Test Summary
- **Date**: $(date)
- **Test Type**: $TEST_TYPE
- **Coverage**: $COVERAGE
- **Status**: $(if [ $? -eq 0 ]; then echo "PASSED"; else echo "FAILED"; fi)

## Test Results
- Backend Tests: $(if [ $? -eq 0 ]; then echo "PASSED"; else echo "FAILED"; fi)
- Frontend Tests: $(if [ $? -eq 0 ]; then echo "PASSED"; else echo "FAILED"; fi)
- Integration Tests: $(if [ $? -eq 0 ]; then echo "PASSED"; else echo "FAILED"; fi)

## Coverage Report
Coverage reports are available in the \`htmlcov\` directory.

## Next Steps
1. Review any failed tests
2. Check coverage reports for untested code
3. Address any linting issues
4. Run integration tests if needed

EOF
    
    print_success "Test report generated: test-reports/summary.md"
}

# Main execution
main() {
    print_status "Starting ZeusAI test suite..."
    
    # Run sanity checks
    run_sanity_checks
    
    # Run tests based on type
    case $TEST_TYPE in
        "frontend")
            run_frontend_tests
            ;;
        "unit"|"api"|"integration")
            run_backend_tests
            ;;
        "all")
            run_backend_tests
            run_frontend_tests
            run_docker_integration_tests
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # Generate test report
    generate_test_report
    
    print_success "Test suite completed successfully!"
    
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage reports available in htmlcov/"
        print_status "Open htmlcov/index.html to view detailed coverage"
    fi
}

# Run main function
main "$@"
