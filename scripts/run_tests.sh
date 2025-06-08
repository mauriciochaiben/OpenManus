#!/bin/bash

# Enhanced test runner that ensures Docker is running and handles all test scenarios
# Usage: ./scripts/run_tests.sh [test_path] [additional_pytest_args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 OpenManus Test Runner${NC}"
echo -e "${BLUE}=================================${NC}"

# Ensure Docker is running for sandbox tests
"$SCRIPT_DIR/ensure_docker.sh"

# Change to project directory
cd "$PROJECT_ROOT"

# Default test path
TEST_PATH=${1:-"tests/"}
shift || true  # Remove first argument if it exists

# Function to run tests with proper configuration
run_tests() {
    local test_path="$1"
    shift
    local extra_args=("$@")

    echo -e "\n${BLUE}📋 Running tests: ${test_path}${NC}"

    # Check if we're running sandbox tests specifically
    if [[ "$test_path" == *"sandbox"* ]]; then
        echo -e "${YELLOW}🐳 Running Docker-dependent sandbox tests...${NC}"
    fi

    # Run tests with coverage and verbose output
    python -m pytest "$test_path" \
        -v \
        --tb=short \
        --cov=app \
        --cov-report=term-missing \
        --cov-report=xml \
        "${extra_args[@]}"
}

# Function to handle test results
handle_results() {
    local exit_code=$1

    if [ $exit_code -eq 0 ]; then
        echo -e "\n${GREEN}✅ All tests passed!${NC}"

        # Check if coverage report was generated
        if [ -f "coverage.xml" ]; then
            echo -e "${GREEN}📊 Coverage report generated: coverage.xml${NC}"
        fi
    else
        echo -e "\n${RED}❌ Some tests failed (exit code: $exit_code)${NC}"

        # Provide helpful suggestions
        echo -e "${YELLOW}💡 Troubleshooting tips:${NC}"
        echo -e "   • For Docker-related failures: Ensure Docker Desktop is running"
        echo -e "   • For import errors: Check if all dependencies are installed"
        echo -e "   • For specific test failures: Run with -vv for more detailed output"
        echo -e "   • To run only failed tests: Use --lf (last failed) flag"
    fi

    return $exit_code
}

# Main execution
echo -e "${BLUE}🎯 Test target: ${TEST_PATH}${NC}"

# Run the tests
if run_tests "$TEST_PATH" "$@"; then
    handle_results 0
else
    handle_results $?
fi
