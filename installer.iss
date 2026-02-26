; NimaStartUpSocial Inno Setup Script

[Setup]
AppId={{D8C9B2E5-F123-4A57-90D0-7D24038A370D}
AppName=NimaStartUpSocial
AppVersion=1.7.0
AppPublisher=NimaTechVibe
DefaultDirName={autopf}\NimaStartUpSocial
DefaultGroupName=NimaStartUpSocial
AllowNoIcons=yes
; Optimization for Python 3.14 stability
Compression=lzma
SolidCompression=yes
WizardStyle=modern
OutputDir=installer_output
OutputBaseFilename=Setup_NimaStartUpSocial
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\NimaStartUpSocial.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "إضافة اختصار إلى قائمة البدء (Start Menu)"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "E:\NimaTechVibeCoding\NimaStartUpSocial\dist\NimaStartUpSocial.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include assets and logs folder if needed, though PyInstaller bundled them
; Source: "E:\NimaTechVibeCoding\NimaStartUpSocial\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NimaStartUpSocial"; Filename: "{app}\NimaStartUpSocial.exe"; Tasks: startmenuicon
Name: "{autodesktop}\NimaStartUpSocial"; Filename: "{app}\NimaStartUpSocial.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\NimaStartUpSocial.exe"; Description: "{cm:LaunchProgram,NimaStartUpSocial}"; Flags: nowait postinstall skipifsilent
