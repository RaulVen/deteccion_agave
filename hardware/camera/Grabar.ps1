param([string]$IP = '', [int]$Segundos = 0)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$options = @('camera.py')
if ($IP) { $options += @('--ip', $IP) }
if ($Segundos -gt 0) { $options += @('--seconds', "$Segundos") }
& python @options
if ($LASTEXITCODE -ne 0) { throw 'La grabacion no pudo iniciarse. Revisa el mensaje anterior.' }
