# Start the authorized resolution and box-loss experiments in a hidden process.
$ErrorActionPreference = 'Stop'
$CampaignRoot = Split-Path -Parent $PSScriptRoot
$CampaignPython = Join-Path $CampaignRoot '.venv\Scripts\python.exe'
$CampaignScript = Join-Path $PSScriptRoot 'train_campaign_opciones34_150.py'
$CampaignDir = Join-Path $CampaignRoot 'benchmark\agave_maleza_150ep_opciones34_2026-10-22'
$CampaignLogDir = Join-Path $CampaignDir 'launcher_logs'

foreach ($CampaignRequired in @($CampaignPython, $CampaignScript)) {
    if (-not (Test-Path -LiteralPath $CampaignRequired -PathType Leaf)) {
        throw "Required file does not exist: $CampaignRequired"
    }
}
New-Item -ItemType Directory -Path $CampaignLogDir -Force | Out-Null
$CampaignLaunchLock = Join-Path $CampaignDir '.launcher.lock'
$CampaignLockStream = [System.IO.File]::Open($CampaignLaunchLock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
try {
    $CampaignMarker = Join-Path $CampaignDir 'launch.json'
    if (Test-Path -LiteralPath $CampaignMarker) {
        throw "This campaign has already been launched. Inspect launch.json and status before attempting recovery."
    }
    $CampaignStamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
    $CampaignOut = Join-Path $CampaignLogDir ($CampaignStamp + '_stdout.log')
    $CampaignErr = Join-Path $CampaignLogDir ($CampaignStamp + '_stderr.log')
    $CampaignArgs = @('-u', '-B', ('"{0}"' -f $CampaignScript), '--run')
    $CampaignProcess = Start-Process -FilePath $CampaignPython -ArgumentList $CampaignArgs -WorkingDirectory $CampaignRoot -WindowStyle Hidden -RedirectStandardOutput $CampaignOut -RedirectStandardError $CampaignErr -PassThru
    $CampaignRecord = [ordered]@{
        pid = $CampaignProcess.Id
        started_utc = [DateTime]::UtcNow.ToString('o')
        python = $CampaignPython
        script = $CampaignScript
        arguments = @('--run')
        stdout = $CampaignOut
        stderr = $CampaignErr
        epochs_each = 150
        order = @('yolo26s_sgd_960_150e', 'yolo26s_sgd_box9_640_150e')
    }
    $CampaignRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $CampaignMarker -Encoding utf8
    $CampaignRecord | ConvertTo-Json -Depth 4
} finally {
    $CampaignLockStream.Dispose()
    Remove-Item -LiteralPath $CampaignLaunchLock
}
