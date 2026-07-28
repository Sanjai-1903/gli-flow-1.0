#!/bin/bash
set -euo pipefail

echo "========================================="
echo "GLI-FLOW Environment Validation"
echo "========================================="
echo ""

echo "[1/5] Checking Python..."
python3 --version

echo ""
echo "[2/5] Checking Docker..."
docker --version

echo ""
echo "[3/5] Checking Git..."
git --version

echo ""
echo "[4/5] Checking LibreLane..."
if command -v librelane &> /dev/null; then
    echo "LibreLane detected"
else
    echo "LibreLane not detected"
fi

echo ""
echo "[5/5] Checking Repository Structure..."

required_dirs=(
    "analytics"
    "execution"
    "telemetry"
    "outputs"
    "configs"
    "docs"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "[OK] $dir"
    else
        echo "[MISSING] $dir"
    fi
done

echo ""
echo "========================================="
echo "Validation Complete"
echo "========================================="
