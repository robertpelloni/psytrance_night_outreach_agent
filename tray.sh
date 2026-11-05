#!/bin/bash
# Autonomous Development Protocol: System Tray & Companion Daemon Launcher

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

export PYTHONPATH=$PYTHONPATH:.
python3 src/dashboard/tray.py "$@"
