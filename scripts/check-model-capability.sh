#!/bin/bash
# Check if a local model can follow JSON schemas before using it.
# Usage: check-model-capability.sh <port> <model-name>

set -uo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <port> <model-name>"
    echo "Example: $0 8099 qwen2.5-1.5b-instruct-q5_k_m.gguf"
    exit 1
fi

PORT="$1"
MODEL="$2"

echo "=== Checking model capability ==="
echo "Port: $PORT"
echo "Model: $MODEL"
echo ""

# Test 1: Can the model follow a JSON schema?
echo "Test 1: JSON schema following..."
RESULT=$(curl -s -m 30 http://127.0.0.1:$PORT/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Respond with JSON only: {\\\"test\\\": \\\"value\\\", \\\"number\\\": 42}\"}],
        \"max_tokens\": 50,
        \"temperature\": 0
    }" 2>&1)

if echo "$RESULT" | grep -q '"test"'; then
    echo "✓ Model can follow JSON schema"
    JSON_OK=1
else
    echo "✗ Model cannot follow JSON schema"
    JSON_OK=0
fi

# Test 2: Can the model switch between schemas?
echo ""
echo "Test 2: Schema switching..."
RESULT2=$(curl -s -m 30 http://127.0.0.1:$PORT/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Respond with JSON: {\\\"label\\\": \\\"A\\\", \\\"confidence\\\": 0.95}\"}],
        \"max_tokens\": 50,
        \"temperature\": 0
    }" 2>&1)

if echo "$RESULT2" | grep -q '"label"'; then
    echo "✓ Model can switch schemas"
    SWITCH_OK=1
else
    echo "✗ Model cannot switch schemas"
    SWITCH_OK=0
fi

# Test 3: Response time
echo ""
echo "Test 3: Response time..."
START=$(date +%s%N)
curl -s -m 30 http://127.0.0.1:$PORT/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Say hello\"}],
        \"max_tokens\": 10,
        \"temperature\": 0
    }" > /dev/null 2>&1
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))
echo "Response time: ${ELAPSED}ms"

if [ $ELAPSED -lt 5000 ]; then
    echo "✓ Response time acceptable (< 5s)"
    TIME_OK=1
else
    echo "✗ Response time too slow (> 5s)"
    TIME_OK=0
fi

echo ""
echo "=== Results ==="
echo "JSON schema: $([ $JSON_OK -eq 1 ] && echo 'PASS' || echo 'FAIL')"
echo "Schema switching: $([ $SWITCH_OK -eq 1 ] && echo 'PASS' || echo 'FAIL')"
echo "Response time: $([ $TIME_OK -eq 1 ] && echo 'PASS' || echo 'FAIL')"

if [ $JSON_OK -eq 1 ] && [ $SWITCH_OK -eq 1 ] && [ $TIME_OK -eq 1 ]; then
    echo ""
    echo "Model is suitable for automated tasks"
    exit 0
else
    echo ""
    echo "Model is NOT suitable for automated tasks"
    exit 1
fi
