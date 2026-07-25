# ============================================================
#  Graveyard Mining - Single-Command Startup Script
#  Usage: .\start.ps1
#  Starts both the FastAPI backend (port 8000) and
#  the Next.js frontend (port 3000) concurrently.
# ============================================================

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$Root     = $PSScriptRoot
$Backend  = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

# ── ANSI colours ─────────────────────────────────────────────
function Write-Color([string]$Text, [string]$Color = "White") {
    $colors = @{ Cyan = "`e[36m"; Green = "`e[32m"; Yellow = "`e[33m"; Red = "`e[31m"; Gray = "`e[90m"; Reset = "`e[0m"; Bold = "`e[1m" }
    Write-Host "$($colors[$Color])$Text$($colors['Reset'])"
}

function Write-Banner {
    Write-Host ""
    Write-Color "  ╔══════════════════════════════════════════════╗" "Cyan"
    Write-Color "  ║       GRAVEYARD MINING  ☠  LAUNCHER          ║" "Cyan"
    Write-Color "  ║   Backend → http://localhost:8000/docs        ║" "Gray"
    Write-Color "  ║   Frontend → http://localhost:3000            ║" "Gray"
    Write-Color "  ╚══════════════════════════════════════════════╝" "Cyan"
    Write-Host ""
}

# ── Pre-flight checks ─────────────────────────────────────────
function Assert-Command([string]$Cmd, [string]$InstallHint) {
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        Write-Color "✗ '$Cmd' not found. $InstallHint" "Red"
        exit 1
    }
}

function Assert-EnvFile {
    $envFile = Join-Path $Backend ".env"
    if (-not (Test-Path $envFile)) {
        Write-Color "✗ backend/.env not found. Copy backend/.env.example and fill in your keys." "Red"
        exit 1
    }
}

# ── Kill children on Ctrl+C ──────────────────────────────────
$BackendJob  = $null
$FrontendJob = $null

function Stop-All {
    Write-Host ""
    Write-Color "⏹  Shutting down..." "Yellow"
    if ($BackendJob)  { Stop-Job  $BackendJob  -ErrorAction SilentlyContinue; Remove-Job $BackendJob  -Force -ErrorAction SilentlyContinue }
    if ($FrontendJob) { Stop-Job  $FrontendJob -ErrorAction SilentlyContinue; Remove-Job $FrontendJob -Force -ErrorAction SilentlyContinue }
    # Kill any lingering uvicorn / node processes on our ports
    $toKill = @()
    $toKill += Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    $toKill += Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    $toKill | Where-Object { $_ -gt 0 } | Sort-Object -Unique | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
    Write-Color "✓  All services stopped." "Green"
    exit 0
}

# Register cleanup on exit
$null = Register-EngineEvent -SourceIdentifier ([System.Management.Automation.PsEngineEvent]::Exiting) -Action { Stop-All }

# ── Wait for a port to respond ───────────────────────────────
function Wait-Port([int]$Port, [string]$Label, [int]$TimeoutSec = 30) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    Write-Color "  ⏳ Waiting for $Label on port $Port..." "Gray"
    while ((Get-Date) -lt $deadline) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $Port)
            $tcp.Close()
            return $true
        } catch { Start-Sleep -Milliseconds 500 }
    }
    return $false
}

# ─────────────────────────────────────────────────────────────
Write-Banner

# Pre-flight
Assert-Command "python"  "Install Python 3.10+ from https://python.org"
Assert-Command "npm"     "Install Node.js 18+ from https://nodejs.org"
Assert-EnvFile

# ── Backend ──────────────────────────────────────────────────
if (-not $FrontendOnly) {
    Write-Color "▶  Starting FastAPI backend..." "Cyan"

    # Install Python deps silently if needed
    $pipCheck = python -c "import fastapi" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Color "  📦 Installing Python dependencies..." "Yellow"
        python -m pip install -r "$Backend\requirements.txt" --quiet
    }

    $BackendJob = Start-Job -Name "Backend" -ScriptBlock {
        param($dir)
        Set-Location $dir
        python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload 2>&1
    } -ArgumentList $Backend

    if (Wait-Port 8000 "Backend") {
        Write-Color "  ✓ Backend is live → http://localhost:8000/docs" "Green"
    } else {
        Write-Color "  ✗ Backend failed to start in time. Check logs below." "Red"
    }
}

# ── Frontend ─────────────────────────────────────────────────
if (-not $BackendOnly) {
    Write-Color "▶  Starting Next.js frontend..." "Cyan"

    # Install npm deps if node_modules is missing
    if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
        Write-Color "  📦 Installing npm dependencies..." "Yellow"
        Push-Location $Frontend
        npm install --silent
        Pop-Location
    }

    $FrontendJob = Start-Job -Name "Frontend" -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm run dev 2>&1
    } -ArgumentList $Frontend

    if (Wait-Port 3000 "Frontend") {
        Write-Color "  ✓ Frontend is live → http://localhost:3000" "Green"
    } else {
        Write-Color "  ✗ Frontend failed to start in time. Check logs below." "Red"
    }
}

# ── Open browser ──────────────────────────────────────────────
if (-not $NoBrowser -and -not $BackendOnly) {
    Start-Sleep -Milliseconds 500
    Start-Process "http://localhost:3000"
}

# ── Live log streaming ────────────────────────────────────────
Write-Host ""
Write-Color "━━━━━━━━━━━━━━  LIVE LOGS  (Ctrl+C to stop)  ━━━━━━━━━━━━━━" "Gray"
Write-Host ""

try {
    while ($true) {
        # Stream backend logs
        if ($BackendJob) {
            $logs = Receive-Job $BackendJob -ErrorAction SilentlyContinue
            foreach ($line in $logs) {
                Write-Color "[API] " "Cyan"
                Write-Host -NoNewline $line
                Write-Host ""
            }
            if ($BackendJob.State -eq "Failed") {
                Write-Color "[API] Job failed unexpectedly." "Red"
            }
        }

        # Stream frontend logs
        if ($FrontendJob) {
            $logs = Receive-Job $FrontendJob -ErrorAction SilentlyContinue
            foreach ($line in $logs) {
                Write-Color "[WEB] " "Yellow"
                Write-Host -NoNewline $line
                Write-Host ""
            }
            if ($FrontendJob.State -eq "Failed") {
                Write-Color "[WEB] Job failed unexpectedly." "Red"
            }
        }

        Start-Sleep -Milliseconds 300
    }
} finally {
    Stop-All
}
