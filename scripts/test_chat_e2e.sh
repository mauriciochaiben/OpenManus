#!/bin/bash

# OpenManus Chat Integration End-to-End Test Script

echo "🚀 Starting OpenManus Chat Integration Tests..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS:${NC} $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL:${NC} $2"
        ((TESTS_FAILED++))
    fi
}

echo -e "${BLUE}🔍 Testing Backend API Health...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:8000/api/v2/system/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_result 0 "Backend API Health Check"
else
    print_result 1 "Backend API Health Check - Response: $HEALTH_RESPONSE"
fi

echo -e "${BLUE}💬 Testing Chat API...${NC}"
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from test script", "context": {}}')

if echo "$CHAT_RESPONSE" | grep -q "id"; then
    print_result 0 "Chat API Message Send"
    echo "   Response: $(echo $CHAT_RESPONSE | jq -r '.message' | head -c 100)..."
else
    print_result 1 "Chat API Message Send - Response: $CHAT_RESPONSE"
fi

echo -e "${BLUE}📝 Testing Chat History...${NC}"
HISTORY_RESPONSE=$(curl -s "http://localhost:8000/api/v2/chat/history?session_id=default")
MESSAGE_COUNT=$(echo "$HISTORY_RESPONSE" | jq 'length' 2>/dev/null || echo "0")

if [ "$MESSAGE_COUNT" -gt 0 ]; then
    print_result 0 "Chat History Retrieval ($MESSAGE_COUNT messages)"
else
    print_result 1 "Chat History Retrieval - No messages found"
fi

echo -e "${BLUE}🔌 Testing WebSocket Endpoint...${NC}"
# Test WebSocket endpoint accessibility (not full connection due to bash limitations)
WS_TEST=$(curl -s -I -H "Connection: Upgrade" -H "Upgrade: websocket" "http://localhost:8000/api/v2/chat/ws/test" 2>&1)
if echo "$WS_TEST" | grep -q "400\|101"; then
    print_result 0 "WebSocket Endpoint Accessible"
else
    print_result 1 "WebSocket Endpoint Not Accessible"
fi

echo -e "${BLUE}🌐 Testing Frontend Server...${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
if [ "$FRONTEND_STATUS" = "200" ]; then
    print_result 0 "Frontend Server Running"
else
    print_result 1 "Frontend Server Not Accessible (Status: $FRONTEND_STATUS)"
fi

echo -e "${BLUE}🔄 Testing CORS Headers...${NC}"
CORS_TEST=$(curl -s -H "Origin: http://localhost:3001" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type" -X OPTIONS "http://localhost:8000/api/v2/chat")
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Origin\|200"; then
    print_result 0 "CORS Headers Configured"
else
    print_result 1 "CORS Headers Not Properly Configured"
fi

echo -e "${BLUE}🧪 Testing Context-Aware Responses...${NC}"
# Test different keywords to verify context-aware responses
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "criar tarefa", "context": {}}' | jq -r '.suggestions[0]' 2>/dev/null)

if [ "$TASK_RESPONSE" != "null" ] && [ -n "$TASK_RESPONSE" ]; then
    print_result 0 "Context-Aware Task Creation Response"
else
    print_result 1 "Context-Aware Task Creation Response"
fi

AGENTS_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "agentes", "context": {}}' | jq -r '.message' 2>/dev/null)

if echo "$AGENTS_RESPONSE" | grep -q "Manus Agent"; then
    print_result 0 "Context-Aware Agents Response"
else
    print_result 1 "Context-Aware Agents Response"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Chat integration is working correctly.${NC}"
    echo ""
    echo -e "${YELLOW}🔗 Next Steps:${NC}"
    echo "1. Open frontend at: http://localhost:3001"
    echo "2. Test chat interface manually"
    echo "3. Verify WebSocket real-time updates"
    echo "4. Test different message contexts"
else
    echo -e "${RED}⚠️  Some tests failed. Please check the issues above.${NC}"
fi

echo ""
echo -e "${BLUE}📊 Test Summary:${NC}"
echo "- Backend API: $([ $(curl -s "http://localhost:8000/api/v2/system/health" | grep -c "healthy") -gt 0 ] && echo "✅ Running" || echo "❌ Down")"
echo "- Frontend: $([ $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001) = "200" ] && echo "✅ Running" || echo "❌ Down")"
echo "- Chat API: $([ $(curl -s -X POST "http://localhost:8000/api/v2/chat" -H "Content-Type: application/json" -d '{"message":"test","context":{}}' | grep -c "id") -gt 0 ] && echo "✅ Working" || echo "❌ Not Working")"
echo ""
echo "🌟 Ready for manual testing at http://localhost:3001"
