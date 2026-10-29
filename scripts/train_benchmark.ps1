# Wrapper: always use this repository's locked Python environment.
$ErrorActionPreference = 'Stop'
$BenchmarkRepoRoot = Split-Path -Parent $PSScriptRoot
$BenchmarkPython = Join-Path $BenchmarkRepoRoot '.venv\Scripts\python.exe'
$BenchmarkScript = Join-Path $PSScriptRoot 'train_benchmark.py'
if (-not (Test-Path -LiteralPath $BenchmarkPython -PathType Leaf)) {
    throw "Missing repository environment: $BenchmarkPython"
}
& $BenchmarkPython -B $BenchmarkScript @args
exit $LASTEXITCODE
