param([string]$IP = '192.168.1.107')
Set-Location $PSScriptRoot
python camera.py --ip $IP --fixed-camera
