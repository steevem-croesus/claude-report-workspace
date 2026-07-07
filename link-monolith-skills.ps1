<#
.SYNOPSIS
    Symlink a curated subset of the monolith's Claude skills into this workspace.

.DESCRIPTION
    Creates directory *symbolic links* (not copies, not junctions) under
    .claude\skills\ pointing at the real skills in the CFF monolith, so Claude Code
    discovers them here and edits in the monolith flow through live.

    Directory symlinks require elevation on Windows (SeCreateSymbolicLinkPrivilege),
    hence this script self-elevates. Re-running is safe: existing links/dirs for the
    listed skills are removed and recreated.

.NOTES
    After it finishes, restart Claude Code so it re-scans .claude\skills\.
    The linked names are gitignored (see .gitignore) - machine-specific links
    are not committed.
#>

$ErrorActionPreference = 'Stop'

# --- self-elevate ---------------------------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Not elevated - relaunching as administrator..." -ForegroundColor Yellow
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', $PSCommandPath
    )
    return
}

# --- config ---------------------------------------------------------------
$Source = 'C:\Repos\monolith\.claude\skills'
$Dest = Join-Path $PSScriptRoot '.claude\skills'

$Skills = @(
    'croesus-orm',
    'create-small-tests',
    'create-medium-tests',
    'create-large-tests',
    'create-internal-route',
    'implement-full-story',
    'croesus-process-conventions'
)

# --- sanity checks --------------------------------------------------------
if (-not (Test-Path -LiteralPath $Source)) { throw "Source not found: $Source" }
if (-not (Test-Path -LiteralPath $Dest))   { throw "Dest not found:   $Dest" }

Write-Host "Source: $Source"
Write-Host "Dest:   $Dest"
Write-Host ""

# --- link each skill ------------------------------------------------------
foreach ($s in $Skills) {
    $target = Join-Path $Source $s
    $link = Join-Path $Dest $s

    if (-not (Test-Path -LiteralPath $target)) {
        Write-Host ("  SKIP  {0,-30} (no source: {1})" -f $s, $target) -ForegroundColor DarkYellow
        continue
    }

    # Remove any prior copy / junction / link so this is idempotent.
    if (Test-Path -LiteralPath $link) {
        $item = Get-Item -LiteralPath $link -Force
        if ($item.LinkType) { $item.Delete() }                   # symlink or junction
        else { Remove-Item -LiteralPath $link -Recurse -Force }   # real copied dir
    }

    New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
    Write-Host ("  LINK  {0,-30} -> {1}" -f $s, $target) -ForegroundColor Green
}

# --- verify ---------------------------------------------------------------
Write-Host ""
Write-Host "Verification:" -ForegroundColor Cyan
foreach ($s in $Skills) {
    $link = Join-Path $Dest $s
    $item = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType -eq 'SymbolicLink') {
        Write-Host ("  OK    {0,-30} [{1}] -> {2}" -f $s, $item.LinkType, $item.Target)
    }
    else {
        Write-Host ("  FAIL  {0,-30} not a symlink" -f $s) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done. Restart Claude Code so it re-scans .claude\skills\." -ForegroundColor Cyan
