param(
    [string]$RepoPath = "\\wsl$\Ubuntu\home\yaako\projects\whisper-key-yaakov",
    [ValidateSet("cuda", "rocm")]
    [string]$Variant = "cuda",
    [switch]$NoZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python is not in PATH. Install Python 3.11+ and ensure 'python' command works in this PowerShell."
}

if (-not (Test-Path $RepoPath)) {
    throw "RepoPath not found: $RepoPath"
}

$buildScript = Join-Path $RepoPath "py-build\build-windows.ps1"
if (-not (Test-Path $buildScript)) {
    throw "Build script not found: $buildScript"
}

Push-Location $RepoPath
try {
    Write-Host "Building Whisper Key portable app..." -ForegroundColor Cyan
    Write-Host "Repo: $RepoPath" -ForegroundColor Gray
    Write-Host "Variant: $Variant" -ForegroundColor Gray

    if ($NoZip) {
        & $buildScript -Variant $Variant -NoZip
    } else {
        & $buildScript -Variant $Variant
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }

    $version = (Select-String -Path "pyproject.toml" -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
    $suffix = if ($Variant -eq "cuda") { "" } else { "-amd-gpu-rocm" }
    $distDir = Join-Path $RepoPath ("dist\whisper-key-v{0}{1}" -f $version, $suffix)

    Write-Host "Build finished successfully." -ForegroundColor Green
    Write-Host "Output folder: $distDir" -ForegroundColor Green
    Write-Host "Expected exe: $distDir\whisper-key\whisper-key.exe" -ForegroundColor Green
    if (-not $NoZip) {
        Write-Host "Expected zip: $distDir\whisper-key-v$version-windows$suffix.zip" -ForegroundColor Green
    }
}
finally {
    Pop-Location
}
