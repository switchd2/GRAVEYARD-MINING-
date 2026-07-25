# ============================================================
#  Graveyard Mining - Docker Startup Script
#  Usage: .\start-docker.ps1
#  Starts the full stack (PostgreSQL, pgAdmin, Backend, Frontend)
#  using Docker Compose.
# ============================================================

function Write-Color {
    param([string]$Text, [string]$Color = "White")
    $colors = @{ Cyan = "`e[36m"; Green = "`e[32m"; Yellow = "`e[33m"; Red = "`e[31m"; Gray = "`e[90m"; Reset = "`e[0m"; Bold = "`e[1m" }
    Write-Host "$($colors[$Color])$Text$($colors['Reset'])"
}

function Write-Banner {
    Write-Host ""
    Write-Color "  ==============================================" "Cyan"
    Write-Color "     GRAVEYARD MINING DOCKER LAUNCHER           " "Cyan"
    Write-Color "     Frontend -> http://localhost:3000          " "Gray"
    Write-Color "     Backend API -> http://localhost:8000/docs  " "Gray"
    Write-Color "     pgAdmin 4 -> http://localhost:5050         " "Gray"
    Write-Color "  ==============================================" "Cyan"
    Write-Host ""
}

# Pre-flight checks
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Color "Error: 'docker' not found. Please install Docker Desktop." "Red"
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Color "Warning: .env not found at root. Creating from .env.example..." "Yellow"
    Copy-Item ".env.example" ".env"
    Write-Color "Success: .env created. Please update it with your actual API keys." "Green"
}

Write-Banner

Write-Color "Starting Docker Compose stack (building images if necessary)..." "Cyan"
Write-Color "(This might take a few minutes the first time)" "Gray"

# Run docker compose in detached mode
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Color "Error: Failed to start Docker Compose stack." "Red"
    exit 1
}

Write-Host ""
Write-Color "Success: All services started successfully in the background!" "Green"
Write-Color "To view live logs, run: docker compose logs -f" "Gray"
Write-Color "To stop the stack, run: docker compose down" "Gray"

# Optionally open browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
