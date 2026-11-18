<#
.SYNOPSIS
    Create the repos\ symlinks that assemble the report-pipeline codebases in this workspace.

.DESCRIPTION
    Creates directory *symbolic links* under repos\ pointing at the real checkouts:
    the CFF monolith (CroesusServer, ReportServer, ReportFoundations, ReportManagerApi,
    CroesusClient, Foundations) and pf-web.

    Directory symlinks require elevation on Windows (unless Developer Mode is on),
    hence this script self-elevates. Re-running is safe: existing links are replaced.
    A real directory sitting at a link path is never deleted - it is reported and skipped.

.PARAMETER MonolithRoot
    Root of the monolith checkout. Default: C:\Repos\monolith

.PARAMETER PfWebRoot
    Root of the pf-web checkout. Default: C:\Repos\pf-web

.EXAMPLE
    .\link-repos.ps1
    .\link-repos.ps1 -MonolithRoot D:\src\monolith -PfWebRoot D:\src\pf-web

.NOTES
    repos\ is gitignored - the links are machine-specific and never committed.
#>

param(
    [string]$MonolithRoot = 'C:\Repos\monolith',
    [string]$PfWebRoot = 'C:\Repos\pf-web'
)

$ErrorActionPreference = 'Stop'

# --- self-elevate ---------------------------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Not elevated - relaunching as administrator..." -ForegroundColor Yellow
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', "`"$PSCommandPath`"",
        '-MonolithRoot', "`"$MonolithRoot`"", '-PfWebRoot', "`"$PfWebRoot`""
    )
    return
}

# --- config ---------------------------------------------------------------
$Dest = Join-Path $PSScriptRoot 'repos'

$Links = [ordered]@{
    'CroesusServer'     = Join-Path $MonolithRoot 'PM\Products\CroesusServer'
    'ReportServer'      = Join-Path $MonolithRoot 'PM\Products\ReportServer'
    'ReportFoundations' = Join-Path $MonolithRoot 'CFF\ReportFoundations'
    'ReportManagerApi'  = Join-Path $MonolithRoot 'CFF\Products\ReportManagerApi'
    'CroesusClient'     = Join-Path $MonolithRoot 'CFF\Products\CroesusClient'
    'Foundations'       = Join-Path $MonolithRoot 'CFF\Foundations'
    'pf-web'            = $PfWebRoot
}

if (-not (Test-Path -LiteralPath $Dest)) { New-Item -ItemType Directory -Path $Dest | Out-Null }

Write-Host "Monolith: $MonolithRoot"
Write-Host "pf-web:   $PfWebRoot"
Write-Host "Dest:     $Dest"
Write-Host ""

# --- link each repo -------------------------------------------------------
foreach ($name in $Links.Keys) {
    $target = $Links[$name]
    $link = Join-Path $Dest $name

    if (-not (Test-Path -LiteralPath $target)) {
        Write-Host ("  SKIP  {0,-20} (no source: {1})" -f $name, $target) -ForegroundColor DarkYellow
        continue
    }

    $item = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
    if ($item) {
        if (-not $item.LinkType) {
            Write-Host ("  SKIP  {0,-20} (real directory in the way: {1})" -f $name, $link) -ForegroundColor Red
            continue
        }
        $item.Delete()
    }

    New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
    Write-Host ("  LINK  {0,-20} -> {1}" -f $name, $target) -ForegroundColor Green
}

# --- verify ---------------------------------------------------------------
Write-Host ""
Write-Host "Verification:" -ForegroundColor Cyan
foreach ($name in $Links.Keys) {
    $item = Get-Item -LiteralPath (Join-Path $Dest $name) -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType -eq 'SymbolicLink') {
        Write-Host ("  OK    {0,-20} -> {1}" -f $name, $item.Target)
    }
    else {
        Write-Host ("  FAIL  {0,-20} not a symlink" -f $name) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
