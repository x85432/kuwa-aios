#define MyAppName "Kuwa GenAI OS"
#define MyAppVersion "v0.4.0"
#define MyAppPublisher "Kuwa AI"
#define MyAppURL "https://kuwaai.tw/os/intro"
#define MyAppIcon "..\..\src\multi-chat\public\images\kuwa-logo.ico"

[Setup]
AppId={{B37EB0AF-B52C-4200-B80F-671FBCE385DC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:/kuwa/GenAI OS
DefaultGroupName=Kuwa GenAI OS
AllowNoIcons=yes
LicenseFile=../../LICENSE
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=Kuwa-GenAI-OS-Model-Installer
SetupIconFile={#MyAppIcon}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DiskSpanning=yes
DiskSliceSize="2000000000"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesetraditional"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

; Inno Setup supports several languages by default, but Kuwa currently lacks
; translations for these languages. Contributions are welcome.
; Name: "armenian"; MessagesFile: "compiler:Languages\Armenian.isl"
; Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
; Name: "bulgarian"; MessagesFile: "compiler:Languages\Bulgarian.isl"
; Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
; Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
; Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
; Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
; Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
; Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
; Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
; Name: "icelandic"; MessagesFile: "compiler:Languages\Icelandic.isl"
; Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
; Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
; Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
; Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
; Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
; Name: "slovak"; MessagesFile: "compiler:Languages\Slovak.isl"
; Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
; Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
; Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
; Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Components]
Name: "models"; Description: "Model Selection"; Types: full custom;Flags: fixed;
Name: "models\gemma_3_1b_it_q4_0"; Description: "Gemma3 1B QAT Q4"; Types: full compact custom;
Name: "models\llama3_point_1_taide_lx_8_q4_km"; Description: "Llama3.1 TAIDE LX-8_Q4_KM"; Types: custom; ExtraDiskSpaceRequired:5261727040;

[Files]
Source: "..\..\windows\executors\gemma3-1b\gemma-3-1b-it-q4_0.gguf"; DestDir: "{app}\windows\executors\gemma3-1b\"; Flags: ignoreversion; Components: "models\gemma_3_1b_it_q4_0"

Source: "{tmp}\models\Llama-3.1-TAIDE-LX-8B-Chat-Q4_K_M.gguf"; DestDir: "{app}\windows\executors\taide\"; Flags: external; Components: "models\llama3_point_1_taide_lx_8_q4_km"

[Icons]
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Kuwa GenAI OS"; Filename: "{app}\windows\start.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Construct RAG"; Filename: "{app}\windows\construct_rag.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Model Download"; Filename: "{app}\windows\executors\download.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Maintenance Tool"; Filename: "{app}\windows\tool.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Upgrade Kuwa"; Filename: "{app}\windows\update.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{userdesktop}\Kuwa GenAI OS"; Filename: "{app}\windows\start.bat"; WorkingDir: "{app}\windows"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{userdesktop}\Construct RAG"; Filename: "{app}\windows\construct_rag.bat"; WorkingDir: "{app}\windows"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"

[Code]
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then
  begin
    DownloadPage.Clear;

    if WizardIsComponentSelected('models\llama3_point_1_taide_lx_8_q4_km') then
    begin
      DownloadPage.Add(
        'https://huggingface.co/tetf/Llama-3.1-TAIDE-LX-8B-Chat-GGUF/resolve/main/Llama-3.1-TAIDE-LX-8B-Chat-Q4_K_M.gguf?download=true',
        'models\Llama-3.1-TAIDE-LX-8B-Chat-Q4_K_M.gguf',
        ''
      );
    end;

    DownloadPage.Show;

    try
      try
        DownloadPage.Download;
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end
  else
    Result := True;
end;
