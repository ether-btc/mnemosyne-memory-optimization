#!/bin/bash
# Preflight checks for Mnemosyne Operability workflows.
# Run before starting any multi-step process to catch blockers early.
# Exit 0 = all checks passed, exit 1 = one or more checks failed.

set -uo pipefail

PASS=0
FAIL=0

check() {
    local name="$1"
    local command="$2"
    if eval "$command" >/dev/null 2>&1; then
        echo "✓ $name"
        PASS=$((PASS + 1))
    else
        echo "✗ $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Preflight Checks ==="
echo ""

# Disk space (need at least 2GB free)
check "Disk space (>= 2GB free)" "test \$(df -BG / | awk 'NR==2 {print \$4}' | tr -d 'G') -ge 2"

# Network connectivity
check "Network (ping 8.8.8.8)" "ping -c 1 -W 2 8.8.8.8"

# Podman (for container workflows)
check "Podman installed" "command -v podman"

# SSH to a16 (for training workflows)
check "a16 reachable" "ssh -o ConnectTimeout=5 -o BatchMode=yes a16 'echo ok'"

# Local decider-0.8b (for decision workflows)
check "Local decider-0.8b (port 8086)" "curl -s -m 2 http://127.0.0.1:8086/v1/models"

# Local qwen2.5-1.5b (for labeling workflows)
check "Local qwen2.5-1.5b (port 8099)" "curl -s -m 2 http://127.0.0.1:8099/v1/models"

# OpenRouter API key (for hosted decision models)
check "OpenRouter API key" "test -n \"\${OPENROUTER_API_KEY:-}\""

# Git (for filing workflows)
check "Git configured" "git config user.name && git config user.email"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "WARNING: $FAIL check(s) failed. Address these before proceeding."
    exit 1
fi

echo ""
echo "All checks passed. Ready to proceed."
exit 0
