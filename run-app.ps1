$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example. Update NEIS_API_KEY in .env if needed."
}

try {
  docker info | Out-Null
} catch {
  Write-Error "Docker Desktop or the Docker engine is not running. Start Docker Desktop first, then run .\run-app.ps1 again."
  exit 1
}

docker compose up --build
