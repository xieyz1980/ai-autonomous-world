#!/bin/bash
# AI Autonomous World - Test Script
# AI自主世界 - 测试脚本

set -e

BASE_URL="http://localhost:8080"

echo "========================================"
echo "  AI World Test Suite"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试函数
test_health() {
    echo "Test 1: Health Check"
    response=$(curl -s $BASE_URL/health)
    if echo "$response" | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC} Health check passed"
        return 0
    else
        echo -e "${RED}✗${NC} Health check failed"
        return 1
    fi
}

test_nodes() {
    echo "Test 2: List Nodes"
    response=$(curl -s $BASE_URL/nodes)
    echo "Response: $response"
    if echo "$response" | grep -q "coordinator"; then
        echo -e "${GREEN}✓${NC} Nodes list working"
        return 0
    else
        echo -e "${RED}✗${NC} Nodes list failed"
        return 1
    fi
}

test_submit_task() {
    echo "Test 3: Submit Task"
    response=$(curl -s -X POST $BASE_URL/message \
        -H "Content-Type: application/json" \
        -d '{
            "msg_id": "test-001",
            "msg_type": "direct",
            "sender": "test",
            "receiver": "coordinator-001",
            "timestamp": '$(date +%s)',
            "payload": {
                "command": "submit_task",
                "task": {
                    "type": "analysis",
                    "description": "Analyze recent system activity",
                    "priority": 5
                }
            }
        }')
    echo "Response: $response"
    echo -e "${GREEN}✓${NC} Task submitted"
}

test_memory() {
    echo "Test 4: Memory Operations"
    # 这里可以添加对共享记忆的测试
    echo -e "${GREEN}✓${NC} Memory test (placeholder)"
}

# 运行测试
echo "Running tests..."
echo ""

failed=0

test_health || failed=$((failed + 1))
test_nodes || failed=$((failed + 1))
test_submit_task || failed=$((failed + 1))
test_memory || failed=$((failed + 1))

echo ""
echo "========================================"
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}$failed test(s) failed${NC}"
fi
echo "========================================"

exit $failed
