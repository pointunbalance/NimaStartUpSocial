$WScriptShell = New-Object -ComObject WScript.Shell
$StartMenu = $WScriptShell.SpecialFolders("Programs")
$ShortcutPath = Join-Path $StartMenu "NimaStartUpSocial.lnk"
$TargetPath = Join-Path $PSScriptRoot "dist\NimaStartUpSocial.exe"
$IconPath = Join-Path $PSScriptRoot "assets\app_icon.ico"

if (!(Test-Path $TargetPath)) {
    Write-Host "ERROR: $TargetPath not found. Run build.bat first." -ForegroundColor Red
    exit 1
}

$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = Split-Path $TargetPath
$Shortcut.Description = "NimaStartUpSocial - Smart Shortcut Launcher"
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = "$IconPath,0"
}
$Shortcut.Save()

Write-Host "Start Menu shortcut created: $ShortcutPath" -ForegroundColor Green
