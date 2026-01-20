#!/bin/bash
# Python MCP Server Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=== Python MCP Server Setup ==="
echo "Location: $SCRIPT_DIR"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf "$VENV_DIR"
fi

echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies (this may take 3-5 minutes)..."
echo "Installing 60+ packages: numpy, pandas, scipy, matplotlib, and more..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "✓ Setup completed successfully!"
echo ""
echo "Virtual environment: $VENV_DIR"
echo "Python executable: $VENV_DIR/bin/python"
echo ""
echo "To activate manually: source $VENV_DIR/bin/activate"
