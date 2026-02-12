param(
    [string]$RepoPath = (Get-Location).Path,
    [ValidateSet("cpu", "cuda")]
    [string]$Device = "cuda",
    [string]$ModelMultilingual = "small",
    [string]$ModelEnglishOnly = "distil-large-v3.5",
    [switch]$SkipLaunch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$appDataDir = Join-Path $env:APPDATA "whisperkey"
$settingsPath = Join-Path $appDataDir "user_settings.yaml"
$logPath = Join-Path $appDataDir "app.log"
$backupPath = Join-Path $appDataDir ("user_settings.backup.{0}.yaml" -f (Get-Date -Format "yyyyMMdd-HHmmss"))

function Write-TestSettings {
    param(
        [Parameter(Mandatory = $true)][string]$Model
    )

    $yaml = @"
whisper:
  model: $Model
  device: $Device
  compute_type: float16
  language: auto
  sync_with_windows_language: true
  beam_size: 5

hotkey:
  recording_hotkey: ctrl+win
  stop_with_modifier_enabled: false
  auto_enter_enabled: true
  auto_enter_combination: alt
  cancel_combination: esc

clipboard:
  auto_paste: true
  paste_hotkey: ctrl+v
  preserve_clipboard: false
  key_simulation_delay: 0.15

logging:
  level: INFO
  file:
    enabled: true
    filename: app.log
  console:
    enabled: true
    level: INFO

console:
  start_hidden: false
"@

    $yaml | Set-Content -Path $settingsPath -Encoding UTF8
}

function Get-LogRaw {
    if (Test-Path $logPath) {
        return Get-Content -Path $logPath -Raw -ErrorAction SilentlyContinue
    }
    return ""
}

function Assert-NewLogContains {
    param(
        [Parameter(Mandatory = $true)][string]$Before,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$StepName
    )

    $after = Get-LogRaw
    $start = [Math]::Min($Before.Length, $after.Length)
    $delta = $after.Substring($start)

    if ($delta -match $Pattern) {
        Write-Host "[PASS] $StepName" -ForegroundColor Green
        return $true
    }

    Write-Host "[FAIL] $StepName" -ForegroundColor Red
    Write-Host "Expected pattern: $Pattern" -ForegroundColor Yellow
    Write-Host "Recent log tail:" -ForegroundColor Yellow
    if (Test-Path $logPath) {
        Get-Content -Path $logPath -Tail 30
    }
    return $false
}

if (-not (Test-Path $appDataDir)) {
    New-Item -Path $appDataDir -ItemType Directory | Out-Null
}

if (Test-Path $settingsPath) {
    Copy-Item -Path $settingsPath -Destination $backupPath -Force
    Write-Host "Backed up existing settings: $backupPath" -ForegroundColor Cyan
}

Write-TestSettings -Model $ModelMultilingual
Write-Host "Wrote test settings to: $settingsPath" -ForegroundColor Cyan

if (Test-Path $logPath) {
    Clear-Content -Path $logPath
} else {
    New-Item -Path $logPath -ItemType File | Out-Null
}

if (-not $SkipLaunch) {
    $pythonExe = Join-Path $RepoPath ".venv\Scripts\python.exe"
    $entryScript = Join-Path $RepoPath "whisper-key.py"

    if ((Test-Path $pythonExe) -and (Test-Path $entryScript)) {
        $launchCmd = "& `"$pythonExe`" `"$entryScript`""
        Start-Process powershell -ArgumentList @("-NoExit", "-Command", $launchCmd) -WorkingDirectory $RepoPath | Out-Null
        Write-Host "Launched Whisper Key in a new PowerShell window." -ForegroundColor Green
    } else {
        Write-Host "Could not auto-launch app. Run it manually:" -ForegroundColor Yellow
        Write-Host "  cd `"$RepoPath`"" -ForegroundColor Yellow
        Write-Host "  .\.venv\Scripts\python.exe whisper-key.py" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Manual action required now." -ForegroundColor Cyan
Read-Host "Press ENTER after Whisper Key is running and tray icon is visible"

$allPassed = $true

# Step 1: English sync
$before = Get-LogRaw
Write-Host ""
Write-Host "STEP 1: English sync" -ForegroundColor Cyan
Write-Host "1) Focus Notepad text area." -ForegroundColor Gray
Write-Host "2) Switch layout to English (Win+Space)." -ForegroundColor Gray
Write-Host "3) Record with Ctrl+Win, stop with Ctrl+Win, speak short sentence." -ForegroundColor Gray
Read-Host "Press ENTER when done"
$allPassed = (Assert-NewLogContains -Before $before -Pattern "Windows Language Sync detected 'en'" -StepName "English layout detected") -and $allPassed

# Step 2: Hebrew sync
$before = Get-LogRaw
Write-Host ""
Write-Host "STEP 2: Hebrew sync" -ForegroundColor Cyan
Write-Host "1) Focus Notepad text area." -ForegroundColor Gray
Write-Host "2) Switch layout to Hebrew (Win+Space)." -ForegroundColor Gray
Write-Host "3) Record with Ctrl+Win, stop with Ctrl+Win, speak short sentence." -ForegroundColor Gray
Read-Host "Press ENTER when done"
$allPassed = (Assert-NewLogContains -Before $before -Pattern "Windows Language Sync detected 'he'" -StepName "Hebrew layout detected") -and $allPassed

# Step 3: English-only model force
Write-TestSettings -Model $ModelEnglishOnly
Write-Host ""
Write-Host "STEP 3 prep: switched model to English-only '$ModelEnglishOnly' in user settings." -ForegroundColor Cyan
Write-Host "Restart Whisper Key now (close old app window, then launch again)." -ForegroundColor Yellow
Read-Host "Press ENTER after restart"

$before = Get-LogRaw
Write-Host ""
Write-Host "STEP 3: English-only force check" -ForegroundColor Cyan
Write-Host "1) Keep Windows layout on Hebrew." -ForegroundColor Gray
Write-Host "2) Record with Ctrl+Win, stop with Ctrl+Win." -ForegroundColor Gray
Read-Host "Press ENTER when done"
$allPassed = (Assert-NewLogContains -Before $before -Pattern "English-only model language override applied" -StepName "English-only model forced en") -and $allPassed

Write-Host ""
if ($allPassed) {
    Write-Host "All checks passed." -ForegroundColor Green
} else {
    Write-Host "One or more checks failed. See log tail above and rerun after fixes." -ForegroundColor Red
}

$restore = Read-Host "Restore original user_settings.yaml from backup? (y/N)"
if ($restore -match "^[Yy]$" -and (Test-Path $backupPath)) {
    Copy-Item -Path $backupPath -Destination $settingsPath -Force
    Write-Host "Restored original settings." -ForegroundColor Green
} else {
    Write-Host "Kept test settings in place." -ForegroundColor Yellow
}

Write-Host "Log file: $logPath" -ForegroundColor Cyan
