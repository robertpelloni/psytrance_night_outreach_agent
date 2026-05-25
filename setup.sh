#!/bin/bash
# Autonomous Development & Repository Synchronization Protocol: Setup Script

echo "=== Initializing System Environment ==="

# 1. Update system packages (if applicable)
# sudo apt-get update && sudo apt-get install -y git python3-pip

# 2. Setup virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# 4. Install dependencies
echo "Installing application dependencies..."
pip install -r requirements.txt

# 5. Install Playwright browsers
echo "Installing browser binaries..."
playwright install chromium

echo "=== Setup Complete. Ready for autonomous execution. ==="
