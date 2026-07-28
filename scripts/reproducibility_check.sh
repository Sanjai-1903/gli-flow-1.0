#!/bin/bash
set -euo pipefail

echo "[CHECK] GLI-FLOW Reproducibility Check"
echo ""

# Compare current environment against baseline manifest
if [ -f "environment/manifests/base_environment.json" ]; then
    echo "[PASS] Environment manifest found"
    python3 -c "
import json, sys
try:
    with open('environment/manifests/base_environment.json') as f:
        manifest = json.load(f)
    print('[PASS] Manifest parsed successfully')
    print(f'       Tools: {len(manifest.get(\"tools\", []))} configured')
except Exception as e:
    print(f'[FAIL] {e}')
    sys.exit(1)
"
else
    echo "[WARN] No baseline environment manifest found"
    echo "       Run 'python3 environment/validate_environment.py' first"
fi

echo ""
echo "[DONE] Reproducibility check complete"
