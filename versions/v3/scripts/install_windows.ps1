#Requires -Version 5.1
<#
.SYNOPSIS
    openEMIS Windows Installer / Local-Development Setup Script

.DESCRIPTION
    Sets up a local openEMIS development environment on Windows by:
      1. Checking / installing prerequisites (Git, Python 3, Docker Desktop).
      2. Cloning (or updating) the openEMIS repository.
      3. Optionally starting the system via Docker Compose.
      4. Optionally seeding demo data using the bundled generator scripts:
           - scripts\generate_demo_data.py  (students, faculty, classrooms, parents)
           - scripts\seed_erp_data.py       (payslips, LPOs, payment vouchers,
                                             discipline records, progressive assessments)

.PARAMETER RepoPath
    Directory where the openEMIS repository is (or will be) cloned.
    Defaults to "$env:USERPROFILE\openEMIS".

.PARAMETER SkipDocker
    If set, skips the Docker Compose step (useful when running on a plain
    Odoo installation without Docker).

.PARAMETER SeedData
    If set, runs scripts\generate_demo_data.py after the containers are up,
    followed by scripts\seed_erp_data.py to populate ERP/financial data.

.EXAMPLE
    # Interactive install with Docker + seed data
    .\install_windows.ps1 -SeedData

.EXAMPLE
    # Install to a custom path without starting Docker
    .\install_windows.ps1 -RepoPath "D:\Projects\openEMIS" -SkipDocker
#>

[CmdletBinding()]
param (
    [string] $RepoPath   = "$env:USERPROFILE\openEMIS",
    [switch] $SkipDocker,
    [switch] $SeedData
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-OK([string]$Message) {
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warn([string]$Message) {
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

function Test-Command([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Assert-Prerequisite([string]$Command, [string]$InstallHint) {
    if (-not (Test-Command $Command)) {
        Write-Warn "$Command is not installed or not on PATH."
        Write-Host "       $InstallHint" -ForegroundColor Yellow
        Write-Host "       Please install it and re-run this script." -ForegroundColor Yellow
        exit 1
    }
    Write-OK "$Command is available."
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. Check prerequisites
# ─────────────────────────────────────────────────────────────────────────────

Write-Step "Checking prerequisites"

Assert-Prerequisite "git"    "Install Git from https://git-scm.com/download/win"
Assert-Prerequisite "python" "Install Python 3.10+ from https://www.python.org/downloads/"

if (-not $SkipDocker) {
    Assert-Prerequisite "docker" "Install Docker Desktop from https://www.docker.com/products/docker-desktop/"
    Assert-Prerequisite "docker-compose" "Docker Compose is bundled with Docker Desktop. Ensure it is on PATH."
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Clone or update the repository
# ─────────────────────────────────────────────────────────────────────────────

Write-Step "Setting up repository at $RepoPath"

if (Test-Path (Join-Path $RepoPath ".git")) {
    Write-Host "  Repository already exists – pulling latest changes..."
    Push-Location $RepoPath
    git pull --ff-only
    Pop-Location
} else {
    Write-Host "  Cloning openEMIS repository..."
    git clone https://github.com/eodenyire/openEMIS.git $RepoPath
}

Write-OK "Repository is ready."

# ─────────────────────────────────────────────────────────────────────────────
# 3. Generate demo data (optional – can run without Docker)
# ─────────────────────────────────────────────────────────────────────────────

if ($SeedData) {
    Write-Step "Generating demo / seed data"
    Push-Location $RepoPath

    # Step 1 – generate bulk XML demo files (students, faculty, classrooms, parents)
    python scripts\generate_demo_data.py
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Demo data generation returned exit code $LASTEXITCODE"
    } else {
        Write-OK "Demo data XML files generated in each module's demo/ directory."
    }

    # Step 2 – seed ERP / financial data (payslips, LPOs, payment vouchers,
    #           discipline records, progressive assessments) via JSON-RPC
    if (-not $SkipDocker) {
        Write-Host "  Seeding ERP & financial data (waiting for Odoo to be ready)..."
        $MaxWait = 60
        $Elapsed = 0
        do {
            Start-Sleep -Seconds 5
            $Elapsed += 5
            $Health = $null
            try {
                $Health = (Invoke-WebRequest -Uri "http://localhost:8069/web/health" `
                    -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue).StatusCode
            } catch {}
        } while ($Health -ne 200 -and $Elapsed -lt $MaxWait)

        if ($Health -eq 200) {
            python scripts\seed_erp_data.py
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "ERP data seeder returned exit code $LASTEXITCODE"
            } else {
                Write-OK "ERP & financial demo data seeded successfully."
            }
        } else {
            Write-Warn "Odoo health check timed out – skipping ERP data seeding."
            Write-Host "  You can run this manually once Odoo is ready:" -ForegroundColor Gray
            Write-Host "    python scripts\seed_erp_data.py" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Skipping ERP data seeding (SkipDocker flag set)." -ForegroundColor Gray
        Write-Host "  Once Odoo is running, seed ERP data with:" -ForegroundColor Gray
        Write-Host "    python scripts\seed_erp_data.py" -ForegroundColor Gray
    }

    Pop-Location
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Start services via Docker Compose
# ─────────────────────────────────────────────────────────────────────────────

if (-not $SkipDocker) {
    Write-Step "Starting openEMIS via Docker Compose"
    Push-Location $RepoPath

    Write-Host "  Building / pulling images (this may take a few minutes)..."
    docker-compose pull
    docker-compose up -d --build

    if ($LASTEXITCODE -ne 0) {
        Write-Warn "docker-compose up returned exit code $LASTEXITCODE"
        Pop-Location
        exit $LASTEXITCODE
    }

    Write-OK "Containers started."
    Write-Host ""
    Write-Host "  openEMIS is now accessible at http://localhost:8069" -ForegroundColor Green
    Write-Host "  Default admin credentials: admin / admin" -ForegroundColor Green
    Write-Host ""
    Write-Host "  To stop the system run:" -ForegroundColor Gray
    Write-Host "    cd `"$RepoPath`" && docker-compose down" -ForegroundColor Gray

    Pop-Location
} else {
    Write-Step "Skipping Docker Compose (--SkipDocker flag set)"
    Write-Host "  To start manually, run from $RepoPath :"
    Write-Host "    docker-compose up -d" -ForegroundColor Gray
}

Write-Host ""
Write-Host "openEMIS setup complete!" -ForegroundColor Green
