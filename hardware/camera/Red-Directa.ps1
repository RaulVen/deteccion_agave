param([string]$Adaptador = 'Ethernet', [switch]$Restaurar)
# Run only with the camera directly attached. Restore the saved settings before reconnecting a router.
$ErrorActionPreference = 'Stop'
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) { throw 'Abre PowerShell como administrador para configurar Ethernet.' }
$file = Join-Path $PSScriptRoot 'ethernet-anterior.xml'
if ($Restaurar) {
    $saved = Import-Clixml -LiteralPath $file
    $nic = Get-NetAdapter -Name $saved.Name
    if ($nic.InterfaceGuid -ne $saved.Guid) { throw 'El adaptador no coincide con el respaldo.' }
    Get-NetIPAddress -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false
    if ($saved.Dhcp -eq 'Enabled') {
        Set-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -Dhcp Enabled
    } else {
        foreach ($address in $saved.Addresses) {
            New-NetIPAddress -InterfaceIndex $nic.ifIndex -IPAddress $address.IPAddress -PrefixLength $address.PrefixLength | Out-Null
        }
        foreach ($route in $saved.DefaultRoutes) {
            New-NetRoute -InterfaceIndex $nic.ifIndex -DestinationPrefix '0.0.0.0/0' -NextHop $route.NextHop -RouteMetric $route.RouteMetric | Out-Null
        }
    }
    if ($saved.AutomaticMetric -eq 'Disabled') {
        Set-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -AutomaticMetric Disabled -InterfaceMetric $saved.InterfaceMetric
    } else {
        Set-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -AutomaticMetric Enabled
    }
    Remove-Item -LiteralPath $file
    Write-Host 'Ethernet restaurado. Puedes reconectar el router.'
    exit
}
$nic = Get-NetAdapter -Name $Adaptador
if ($nic.Status -ne 'Up') { throw 'Ethernet no tiene enlace. Conecta y alimenta la camara.' }
if (-not (Test-Path -LiteralPath $file)) {
    $ipv4 = Get-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4
    $saved = [pscustomobject]@{
        Name = $nic.Name; Guid = $nic.InterfaceGuid; Dhcp = "$($ipv4.Dhcp)"
        AutomaticMetric = "$($ipv4.AutomaticMetric)"; InterfaceMetric = $ipv4.InterfaceMetric
        Addresses = @(Get-NetIPAddress -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 | Where-Object PrefixOrigin -eq Manual | Select-Object IPAddress,PrefixLength)
        DefaultRoutes = @(Get-NetRoute -InterfaceIndex $nic.ifIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Select-Object NextHop,RouteMetric)
    }
    $saved | Export-Clixml -LiteralPath $file
}
Set-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -Dhcp Disabled
Set-NetIPInterface -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -AutomaticMetric Disabled -InterfaceMetric 1
Get-NetRoute -InterfaceIndex $nic.ifIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Remove-NetRoute -Confirm:$false
Get-NetIPAddress -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false
foreach ($address in @('192.168.1.240','192.168.0.240','10.1.1.240')) {
    New-NetIPAddress -InterfaceIndex $nic.ifIndex -IPAddress $address -PrefixLength 24 | Out-Null
}
Write-Host 'Red local lista. No requiere internet. La camara debe tener IP fija; este script no proporciona DHCP.'
Write-Host 'Ejecuta .\Grabar.ps1. Al terminar, .\Red-Directa.ps1 -Restaurar'
