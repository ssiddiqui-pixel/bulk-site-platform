#!/usr/bin/env bash
# Launch the Bulk Site Builder dashboard.
# Usage:  ANTHROPIC_API_KEY=sk-ant-... ./dashboard/run.sh
set -e
cd "$(dirname "$0")/.."
VENV="dashboard/.venv"
if [ ! -d "$VENV" ]; then
  echo "Creating venv + installing deps…"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip -r dashboard/requirements.txt
fi
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠  ANTHROPIC_API_KEY is not set — the UI will load but builds will fail."
  echo "   Get a key at https://console.anthropic.com and run:"
  echo "   ANTHROPIC_API_KEY=sk-ant-... ./dashboard/run.sh"
fi
exec "$VENV/bin/python" dashboard/app.py
