[Setup]
AppName=NOTEVIL//NET
AppVersion=2.0
DefaultDirName={autopf}\notevil-net
DefaultGroupName=NOTEVIL//NET
UninstallDisplayIcon={app}\notevil-net.exe
OutputDir=.\Output
OutputBaseFilename=notevil-net-setup
SetupIconFile=.\icons\notevil.ico
PrivilegesRequired=admin

[Files]
; Основной экзешник
Source: ".\dist\notevil-net.exe"; DestDir: "{app}"; Flags: ignoreversion
; Папка с ядром sing-box
Source: ".\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs
; Папка с конфигом
Source: ".\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs
; Иконка
Source: ".\icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion

[Icons]
Name: "{group}\NOTEVIL//NET"; Filename: "{app}\notevil-net.exe"
Name: "{commondesktop}\NOTEVIL//NET"; Filename: "{app}\notevil-net.exe"