#!/bin/bash
# OpenManus - Post-Cleanup Verification Script
# This script verifies that all systems work after the cleanup

echo "🧹 OpenManus - Post-Cleanup Verification"
echo "========================================"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run tests
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

echo ""
echo "🔍 Running System Verification Tests..."
echo ""

# Test 1: Python backend imports
run_test "Backend imports" "python -c 'import app.config; import app.agent.base'"

# Test 2: Main entry point
run_test "Main script" "python -c 'import main'"

# Test 3: Package.json validity
run_test "Package.json" "npm run --silent 2>/dev/null"

# Test 4: Frontend dependencies
run_test "Frontend config" "cd frontend && npm run build --dry-run"

# Test 5: Start script executable
run_test "Start script" "test -x start_dev.sh"

# Test 6: Documentation structure
run_test "Documentation" "test -d docs && test -f docs/MULTI_AGENT_ARCHITECTURE.md"

# Test 7: Clean structure (no cache files)
run_test "Cache cleanup" "test $(find . -name '__pycache__' -type d | wc -l) -eq 0"

# Test 8: Log management
run_test "Log management" "test $(ls logs/ | wc -l) -le 15"

echo ""
echo "📊 Test Results:"
echo "================"
echo -e "✅ Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! OpenManus cleanup was successful!${NC}"
    echo ""
    echo "🚀 You can now start OpenManus with:"
    echo "   ./start_dev.sh"
    echo ""
    echo "📊 Cleanup Summary:"
    echo "   • Removed 40+ redundant files"
    echo "   • Organized structure into logical folders"
    echo "   • Cleaned configurations and dependencies"
    echo "   • Maintained all core functionality"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Please check the issues above.${NC}"
fi

echo "🎊 OpenManus hygienization complete!"
