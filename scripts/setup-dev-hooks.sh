#!/bin/bash
# Setup pre-commit hooks to skip on development branch

HOOK_FILE=".git/hooks/pre-commit"

if [ ! -f "$HOOK_FILE" ]; then
    echo "❌ Pre-commit hook not found. Run 'pre-commit install' first."
    exit 1
fi

# Check if already patched
if grep -q "Skip pre-commit hooks on development branch" "$HOOK_FILE"; then
    echo "✅ Pre-commit hook already configured for development branch"
    exit 0
fi

# Add branch check after the shebang and before templated section
sed -i '/^# ID: /a\
\
# Skip pre-commit hooks on development branch\
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)\
if [ "$BRANCH" = "development" ]; then\
    echo "ℹ️  On development branch - skipping pre-commit hooks"\
    exit 0\
fi' "$HOOK_FILE"

echo "✅ Pre-commit hook configured to skip on development branch"
echo "ℹ️  Note: Run this script again after running 'pre-commit install'"
