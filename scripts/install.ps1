# GLI-FLOW One-Command Install (PowerShell)
# Supports: Windows 10/11, WSL2
# Usage: iex (iwr -Uri https://raw.githubusercontent.com/Jegadiswar-SM/gli-flow-asic/main/scripts/install.ps1)

$GLIFlowVersion = "v1.0.0"
$MinPython = "3.9"
$MinDiskGB = 10
$MinRAMMB = 2048

function Write-Pass { Write-Host "  ✓ $($args[0])" -ForegroundColor Green }
function Write-Warn { Write-Host "  ⚠ $($args[0])" -ForegroundColor Yellow }
function Write-Fail { Write-Host "  ✗ $($args[0])" -ForegroundColor Red; exit 1 }
function Write-Info { Write-Host "  → $($args[0])" -ForegroundColor Cyan }

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     GLI-FLOW Installer $GLIFlowVersion        ║" -ForegroundColor Cyan
Write-Host "║  RTL-to-GDS Silicon Pipeline             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ---- OS Detection ----
Write-Info "Detecting operating system..."

$IsWSL = $false
if (Get-ChildItem Env:WSL_DISTRO_NAME -ErrorAction SilentlyContinue) {
    $IsWSL = $true
    Write-Pass "WSL2 detected"
}

if ($IsWSL) {
    Write-Info "Detecting WSL Linux distribution..."
    $osRelease = Get-Content /etc/os-release -ErrorAction SilentlyContinue
    if ($osRelease -match 'ID=ubuntu') {
        Write-Pass "Ubuntu on WSL2 detected"
    } elseif ($osRelease -match 'ID=debian') {
        Write-Pass "Debian on WSL2 detected"
    } else {
        Write-Warn "Untested WSL distribution. Proceeding with caution."
    }
} else {
    $os = (Get-WmiObject Win32_OperatingSystem).Caption
    Write-Pass "Windows detected: $os"
    $majorVer = [Environment]::OSVersion.Version.Major
    if ($majorVer -lt 10) {
        Write-Fail "Windows 10+ required (found version $majorVer)"
    }
}

# ---- Prerequisites ----
Write-Info "Checking prerequisites..."

# Check Python
$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    $p = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($p) { $pythonCmd = $cmd; break }
}

if (-not $pythonCmd) {
    Write-Fail "Python not found. Install Python $MinPython+ from https://python.org"
}

$pyVersion = & $pythonCmd --version 2>&1
if ($pyVersion -match '(\d+)\.(\d+)') {
    $majorPy = [int]$matches[1]
    $minorPy = [int]$matches[2]
    $reqMajor = [int]$MinPython.Split('.')[0]
    $reqMinor = [int]$MinPython.Split('.')[1]
    if ($majorPy -lt $reqMajor -or ($majorPy -eq $reqMajor -and $minorPy -lt $reqMinor)) {
        Write-Fail "Python $MinPython+ required (found $majorPy.$minorPy)"
    }
    Write-Pass "Python $majorPy.$minorPy"
} else {
    Write-Fail "Could not determine Python version"
}

# ---- Disk Space ----
$drive = Get-PSDrive C -ErrorAction SilentlyContinue
if ($drive) {
    $availGB = [math]::Floor($drive.Free / 1GB)
    if ($availGB -lt $MinDiskGB) {
        Write-Fail "Insufficient disk space: ${availGB}GB (need ${MinDiskGB}GB)"
    }
    Write-Pass "Disk space: ${availGB}GB"
}

# ---- RAM ----
$osInfo = Get-WmiObject Win32_ComputerSystem -ErrorAction SilentlyContinue
if ($osInfo) {
    $totalRAMMB = [math]::Floor($osInfo.TotalPhysicalMemory / 1MB)
} else {
    $totalRAMMB = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB
    $totalRAMMB = [math]::Floor($totalRAMMB)
}
if ($totalRAMMB -lt $MinRAMMB) {
    Write-Fail "Insufficient RAM: ${totalRAMMB}MB (need ${MinRAMMB}MB)"
}
Write-Pass "RAM: ${totalRAMMB}MB"

# ---- Docker (optional) ----
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    Write-Pass "Docker found"
} else {
    Write-Warn "Docker not found (optional — needed for containerized runs)"
}

# ---- Install GLI-FLOW ----
Write-Info "Installing gli-flow..."

$PipCmd = "pip3"
if (-not (Get-Command pip3 -ErrorAction SilentlyContinue)) {
    $PipCmd = "pip"
}

# Create virtual environment if not already in one
if (-not $env:VIRTUAL_ENV) {
    $venvDir = "$env:USERPROFILE\.gli-flow\venv"
    if (-not (Test-Path $venvDir)) {
        Write-Info "Creating virtual environment at $venvDir"
        & $pythonCmd -m venv $venvDir
    }
    $activateScript = "$venvDir\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
        $PipCmd = "$venvDir\Scripts\pip"
    }
    Write-Pass "Virtual environment ready"
}

Write-Info "Installing gli-flow package..."
& $PipCmd install --quiet --upgrade pip setuptools wheel 2>$null
& $PipCmd install "gli-flow" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "gli-flow installation failed. Try: pip install gli-flow"
}
Write-Pass "gli-flow installed"

# ---- Run Doctor ----
Write-Info "Running environment validation..."
$gliFlowCmd = Get-Command gli-flow -ErrorAction SilentlyContinue
if ($gliFlowCmd) {
    & gli-flow doctor 2>&1 | Out-Null
    Write-Pass "Environment validated"
} else {
    Write-Warn "gli-flow command not in PATH. Add $venvDir\Scripts to your PATH."
}

# ---- Success ----
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Installation Complete!                  ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Next steps:                             ║" -ForegroundColor Cyan
Write-Host "║                                          ║" -ForegroundColor Cyan
Write-Host "║  gli-flow quickstart                     ║" -ForegroundColor Cyan
Write-Host "║  gli-flow run examples/counter           ║" -ForegroundColor Cyan
Write-Host "║  gli-flow doctor                         ║" -ForegroundColor Cyan
Write-Host "║                                          ║" -ForegroundColor Cyan
Write-Host "║  Docs: https://opencode.ai/gli-flow      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
