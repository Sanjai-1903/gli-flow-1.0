# gli-flow-docker.ps1 — Windows PowerShell wrapper to run gli-flow in Docker.
#
# Mounts your current folder and your ~/.gli-flow login dir into the
# container and forwards the server URLs, so real runs upload to your account.
#
# Usage (from the folder with your design):
#   .\gli-flow-docker.ps1 login
#   .\gli-flow-docker.ps1 init mux --rtl mux.v --sdc mux.sdc
#   .\gli-flow-docker.ps1 run mux
#
# First run pulls the image (~4-6 GB), once.

$ErrorActionPreference = "Stop"

$Image     = if ($env:GLI_FLOW_IMAGE) { $env:GLI_FLOW_IMAGE } else { "sanjaimurugan/gli-flow:latest" }
$IngestUrl = if ($env:GLI_INGEST_URL) { $env:GLI_INGEST_URL } else { "https://gli-flow-1-0-ingest.onrender.com" }
$WebUrl    = if ($env:GLI_WEB_URL)    { $env:GLI_WEB_URL }    else { "https://gli-flow-1-0.vercel.app" }

$AuthDir = Join-Path $HOME ".gli-flow"
if (-not (Test-Path $AuthDir)) { New-Item -ItemType Directory -Path $AuthDir | Out-Null }

docker run --rm -it `
  -v "${PWD}:/work" `
  -v "${AuthDir}:/root/.gli-flow" `
  -e GLI_INGEST_URL="$IngestUrl" `
  -e GLI_WEB_URL="$WebUrl" `
  $Image @args
