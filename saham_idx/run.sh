#!/usr/bin/env bash
# Wrapper for Windows Task Scheduler — logs to ~/saham_idx.log
set -e

# Task Scheduler launches WSL with a minimal env, so uv isn't on PATH.
# Add the usual install locations explicitly.
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

cd "$(dirname "$0")"

LOG_FILE="$HOME/saham_idx.log"

{
  echo ""
  echo "=========================================="
  echo "Run started: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "=========================================="
  uv run main.py
  echo "Run finished: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} >> "$LOG_FILE" 2>&1
