#!/bin/bash

# run_tests.sh - Automated test runner for Soul Foods Dash Application
# This script activates the virtual environment and runs the test suite

# Set strict mode for better error handling
set -e
set -u
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found at .venv"
        print_info "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
        return 1
    else
        print_success "Virtual environment found"
        return 0
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    
    # Check OS and activate accordingly
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        source .venv/Scripts/activate
    else
        # Unix/Linux/MacOS
        source .venv/bin/activate
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment activated"
        return 0
    else
        print_error "Failed to activate virtual environment"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Checking/Installing dependencies..."
    
    # Check if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --quiet
        if [ $? -eq 0 ]; then
            print_success "Dependencies installed/verified"
            return 0
        else
            print_error "Failed to install dependencies"
            return 1
        fi
    else
        print_warning "requirements.txt not found"
        print_info "Installing base dependencies..."
        pip install dash pandas plotly pytest pytest-cov webdriver-manager --quiet
        return $?
    fi
}

# Function to run the test suite
run_tests() {
    print_header "Running Test Suite"
    
    # Run pytest with verbose output
    if [ -f "test_app.py" ]; then
        pytest test_app.py -v --tb=short
        
        # Capture exit code
        TEST_EXIT_CODE=$?
        
        if [ $TEST_EXIT_CODE -eq 0 ]; then
            print_success "All tests passed! 🎉"
            return 0
        else
            print_error "Some tests failed! ❌"
            return 1
        fi
    else
        print_error "test_app.py not found!"
        return 1
    fi
}

# Function to run tests with coverage
run_coverage() {
    print_info "Running tests with coverage..."
    
    if [ -f "test_app.py" ]; then
        pytest test_app.py -v --cov=. --cov-report=term --cov-report=html
        
        if [ $? -eq 0 ]; then
            print_success "Coverage report generated"
            print_info "Open htmlcov/index.html to view detailed report"
            return 0
        else
            print_error "Coverage run failed"
            return 1
        fi
    fi
}

# Function to cleanup
cleanup() {
    print_info "Cleaning up..."
    # Deactivate virtual environment if active
    if [ -n "${VIRTUAL_ENV:-}" ]; then
        deactivate 2>/dev/null || true
        print_success "Virtual environment deactivated"
    fi
}

# Function to check for Chrome/Chromium
check_chrome() {
    print_info "Checking for Chrome browser..."
    
    if command -v google-chrome &> /dev/null; then
        print_success "Google Chrome found"
        CHROME_VERSION=$(google-chrome --version 2>/dev/null | cut -d ' ' -f 3)
        print_info "Chrome version: $CHROME_VERSION"
        return 0
    elif command -v chrome &> /dev/null; then
        print_success "Chrome found"
        return 0
    elif command -v chromium-browser &> /dev/null; then
        print_success "Chromium found"
        return 0
    elif command -v chromium &> /dev/null; then
        print_success "Chromium found"
        return 0
    else
        print_warning "Chrome/Chromium not found! Tests may fail."
        print_info "Please install Chrome or Chromium for headless testing"
        return 1
    fi
}

# Main execution
main() {
    print_header "Soul Foods Dash App - Test Automation"
    
    # Store the script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    # Check Chrome installation
    check_chrome
    
    # Check for virtual environment
    if ! check_venv; then
        print_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    if ! activate_venv; then
        print_error "Failed to activate virtual environment"
        cleanup
        exit 1
    fi
    
    # Install dependencies
    if ! install_dependencies; then
        print_error "Failed to install dependencies"
        cleanup
        exit 1
    fi
    
    # Check if test file exists
    if [ ! -f "test_app.py" ]; then
        print_error "test_app.py not found!"
        cleanup
        exit 1
    fi
    
    # Run the tests
    if run_tests; then
        print_success "✅ All tests passed successfully!"
        EXIT_CODE=0
    else
        print_error "❌ Test suite failed!"
        EXIT_CODE=1
    fi
    
    # Optional: Run coverage
    if [ "${RUN_COVERAGE:-false}" = "true" ]; then
        echo ""
        if run_coverage; then
            print_success "Coverage report generated"
        fi
    fi
    
    # Cleanup
    cleanup
    
    # Return appropriate exit code
    exit $EXIT_CODE
}

# Trap interrupts and cleanup
trap cleanup EXIT INT TERM

# Run main function with all arguments
main "$@"