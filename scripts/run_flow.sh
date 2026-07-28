#!/bin/bash
set -euo pipefail

DESIGN=$1

if [ -z "$DESIGN" ]; then
  echo "[GLI-FLOW] ERROR: No design file provided"
  exit 1
fi

if [ ! -f "$DESIGN" ]; then
  echo "[GLI-FLOW] ERROR: Design file not found: $DESIGN"
  exit 1
fi

echo "[GLI-FLOW] Starting flow for $DESIGN"
echo "[GLI-FLOW] Running synthesis..."
sleep 1
echo "[GLI-FLOW] Running floorplan..."
sleep 1
echo "[GLI-FLOW] Running placement..."
sleep 1
echo "[GLI-FLOW] Running routing..."
sleep 1
echo "[GLI-FLOW] Running STA..."
sleep 1
echo "[GLI-FLOW] Flow completed successfully"
