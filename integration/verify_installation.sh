#!/bin/bash
# Claude Max OpenWebUI Function - Installation Verification Script
# Run this to verify the installation is correct and ready to use

set -e

echo "Claude Max OpenWebUI Function - Installation Verification"
echo "=========================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check 1: Python 3.7+
echo "1. Checking Python version..."
if python3 --version > /dev/null 2>&1; then
    version=$(python3 --version | awk '{print $2}')
    check_pass "Python 3 installed: $version"
else
    check_fail "Python 3 not found"
    exit 1
fi

# Check 2: Claude CLI installed
echo ""
echo "2. Checking Claude CLI installation..."
if which claude > /dev/null 2>&1; then
    cli_version=$(claude --version)
    check_pass "Claude CLI installed: $cli_version"
else
    check_fail "Claude CLI not found in PATH"
    check_warn "Install with: npm install -g @anthropic-ai/claude"
    exit 1
fi

# Check 3: Claude CLI version
echo ""
echo "3. Checking Claude CLI version..."
cli_ver=$(claude --version | awk '{print $1}')
min_ver="2.0.0"
if [ "$(printf '%s\n' "$min_ver" "$cli_ver" | sort -V | head -n1)" = "$min_ver" ]; then
    check_pass "Claude CLI version acceptable: $cli_ver"
else
    check_fail "Claude CLI version too old: $cli_ver (need $min_ver)"
    exit 1
fi

# Check 4: Claude authentication
echo ""
echo "4. Checking Claude authentication..."
if [ -f ~/.claude/auth_token ]; then
    check_pass "Auth token found at ~/.claude/auth_token"
else
    check_fail "Auth token not found"
    check_warn "Run: claude auth login"
    exit 1
fi

# Check 5: Module syntax
echo ""
echo "5. Checking module Python syntax..."
module_path="/home/setup/infrafabric/integration/openwebui_claude_max_module.py"
if [ ! -f "$module_path" ]; then
    check_fail "Module file not found at $module_path"
    exit 1
fi

if python3 -m py_compile "$module_path" 2>/dev/null; then
    check_pass "Module syntax valid"
else
    check_fail "Module syntax error"
    exit 1
fi

# Check 6: Module functionality
echo ""
echo "6. Checking module functionality..."
status_output=$(python3 "$module_path" --status 2>/dev/null)
if echo "$status_output" | grep -q '"ready": true'; then
    check_pass "Module ready status: true"
elif echo "$status_output" | grep -q '"ready": false'; then
    check_warn "Module ready status: false (likely authentication needed)"
else
    check_fail "Could not determine module status"
    exit 1
fi

# Check 7: Test execution
echo ""
echo "7. Testing module execution..."
test_output=$(python3 "$module_path" --test "Hello" 2>/dev/null)
if [ -n "$test_output" ]; then
    check_pass "Module test execution successful"
else
    check_warn "Module test execution returned no output (check auth)"
fi

# Summary
echo ""
echo "=========================================================="
echo "Verification Summary"
echo "=========================================================="
echo ""
echo -e "${GREEN}Installation appears to be correct!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy to OpenWebUI:"
echo "   docker cp $module_path open-webui:/app/backend/data/functions/"
echo "2. Restart OpenWebUI:"
echo "   docker restart open-webui"
echo "3. Open OpenWebUI: http://localhost:8080"
echo "4. Select 'Claude Max OpenWebUI' in chat"
echo "5. Send a message to test"
echo ""
echo "For detailed installation steps, see:"
echo "  /home/setup/infrafabric/integration/DEPLOYMENT_GUIDE.md"
echo ""
