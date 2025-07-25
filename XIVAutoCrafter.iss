; Inno Setup Script for XIVAutoCrafter
; Creates a Windows installer that installs to Program Files\XIVAutoCrafter
; and creates desktop and start menu shortcuts
;
; ⚠️  IMPORTANT: XIVAutoCrafter is FREE SOFTWARE ⚠️
; This software may NEVER be sold or charged for by anyone.
; It must remain free for all users forever.

[Setup]
AppId={{A7B8C9D0-E1F2-4567-8901-234567890ABC}
AppName=XIVAutoCrafter
AppVersion=1.0.0
AppVerName=XIVAutoCrafter 1.0.0
AppPublisher=SolarShards
AppPublisherURL=https://github.com/SolarShards/XIVAutoCrafter
AppSupportURL=https://github.com/SolarShards/XIVAutoCrafter/issues
AppUpdatesURL=https://github.com/SolarShards/XIVAutoCrafter/releases
DefaultDirName={autopf}\XIVAutoCrafter
DefaultGroupName=XIVAutoCrafter
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md
OutputDir=installer
OutputBaseFilename=XIVAutoCrafter-Setup-v1.0.0
; SetupIconFile=icon.ico  ; Uncomment when you have an icon file
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
; Main executable (will be created by PyInstaller)
Source: "dist\XIVAutoCrafter.exe"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

; Python source files (optional, for transparency)
Source: "main.py"; DestDir: "{app}\src"; Flags: ignoreversion
Source: "src\*"; DestDir: "{app}\src\src"; Flags: ignoreversion recursesubdirs createallsubdirs

; Create a placeholder file to ensure user data directory exists
; This also serves as a marker for the data directory location
Source: "README.md"; DestDir: "{code:GetDataDir}"; DestName: "README_DataLocation.txt"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\XIVAutoCrafter"; Filename: "{app}\XIVAutoCrafter.exe"; Comment: "Launch XIVAutoCrafter"
Name: "{group}\XIVAutoCrafter Documentation"; Filename: "{app}\README.md"; Comment: "View XIVAutoCrafter documentation"
Name: "{group}\Open User Data Folder"; Filename: "{code:GetDataDir}"; Comment: "Open folder containing your recipes and settings"
Name: "{group}\{cm:ProgramOnTheWeb,XIVAutoCrafter}"; Filename: "https://github.com/SolarShards/XIVAutoCrafter"
Name: "{group}\{cm:UninstallProgram,XIVAutoCrafter}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional, user can choose during install)
Name: "{autodesktop}\XIVAutoCrafter"; Filename: "{app}\XIVAutoCrafter.exe"; Comment: "Launch XIVAutoCrafter"; Tasks: desktopicon

; Quick Launch shortcut (for older Windows versions)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\XIVAutoCrafter"; Filename: "{app}\XIVAutoCrafter.exe"; Tasks: quicklaunchicon

[Registry]
; Register the application for proper Windows integration
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-4567-8901-234567890ABC}_is1"; ValueType: string; ValueName: "DisplayName"; ValueData: "XIVAutoCrafter"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-4567-8901-234567890ABC}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "1.0.0"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-4567-8901-234567890ABC}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "SolarShards"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-4567-8901-234567890ABC}_is1"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "https://github.com/SolarShards/XIVAutoCrafter"; Flags: uninsdeletekey

; Store user data directory location for future reference
Root: HKCU; Subkey: "Software\XIVAutoCrafter"; ValueType: string; ValueName: "UserDataPath"; ValueData: "{code:GetDataDir}"; Flags: uninsdeletevalue

[Run]
; Option to launch the application after installation
Filename: "{app}\XIVAutoCrafter.exe"; Description: "{cm:LaunchProgram,XIVAutoCrafter}"; Flags: nowait postinstall skipifsilent

[Code]
var
  UserDataDir: string;

function InitializeSetup(): Boolean;
begin
  Result := True;
  UserDataDir := ExpandConstant('{userappdata}\XIVAutoCrafter');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create user data directory in AppData if needed
    if not DirExists(UserDataDir) then
      CreateDir(UserDataDir);
  end;
end;

function GetDataDir(Param: string): string;
begin
  Result := UserDataDir;
end;
