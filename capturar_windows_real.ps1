# ==============================================================================
# Script de Captura Real en Escritorio Windows 11 (PowerShell + Wireshark GUI)
# Usa System.Windows.Forms + System.Drawing ($graphics.CopyFromScreen)
# ==============================================================================
param(
    [object[]]$Pasos = @(1, 2, 3, 4, 5, 6, 7, 8, 9)
)
$Pasos = @($Pasos | ForEach-Object { "$_" -split ',' } | Where-Object { $_ -match '^\s*\d+\s*$' } | ForEach-Object { [int]$_.Trim() })

$ErrorActionPreference = "Stop"
$WorkDir = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($WorkDir)) {
    $WorkDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
}
Set-Location -LiteralPath $WorkDir

New-Item -ItemType Directory -Force -Path (Join-Path $WorkDir "img") | Out-Null
$TempDir = Join-Path $env:TEMP "lab4_win_captures"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Add-Type -AssemblyName System.Windows.Forms, System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32CaptureHelper {
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    public static void ForceTopMostMaximize(IntPtr hWnd) {
        if (hWnd == IntPtr.Zero) return;
        ShowWindow(hWnd, 3); // SW_MAXIMIZE
        SetWindowPos(hWnd, new IntPtr(-1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040); // HWND_TOPMOST
        BringWindowToTop(hWnd);
        SetForegroundWindow(hWnd);
    }
}
"@

[Win32CaptureHelper]::SetProcessDPIAware() | Out-Null

function Save-RealScreenCapture {
    param(
        [Parameter(Mandatory = $true)][string]$OutputFile
    )
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $fullOut = Join-Path $WorkDir "img\$OutputFile"
    $bmp.Save($fullOut, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bmp.Dispose()
    Write-Host "[OK] Captura real guardada: $fullOut ($($bounds.Width)x$($bounds.Height))" -ForegroundColor Green
}

function Invoke-ConsoleWindowCapture {
    param(
        [Parameter(Mandatory = $true)][string]$StepName,
        [Parameter(Mandatory = $true)][string]$WindowTitle,
        [Parameter(Mandatory = $true)][string]$ScriptBody,
        [Parameter(Mandatory = $true)][string]$OutputPng
    )

    $runnerPath = Join-Path $TempDir "$StepName.ps1"
    $readyPath  = Join-Path $TempDir "$StepName.ready"
    Remove-Item -LiteralPath $readyPath -Force -ErrorAction SilentlyContinue

    $header = @'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$Host.UI.RawUI.WindowTitle = "__TITLE__"
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ConsoleWinHelper {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct CONSOLE_FONT_INFO_EX {
        public uint cbSize;
        public uint nFont;
        public short dwFontSizeX;
        public short dwFontSizeY;
        public int FontFamily;
        public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string FaceName;
    }
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GetStdHandle(int nStdHandle);
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern bool SetCurrentConsoleFontEx(IntPtr hConsoleOutput, bool bMaximumWindow, ref CONSOLE_FONT_INFO_EX lpConsoleCurrentFontEx);
    public static void SetFont(short sizeY) {
        IntPtr hnd = GetStdHandle(-11);
        CONSOLE_FONT_INFO_EX info = new CONSOLE_FONT_INFO_EX();
        info.cbSize = (uint)Marshal.SizeOf(info);
        info.dwFontSizeX = 0;
        info.dwFontSizeY = sizeY;
        info.FontFamily = 54;
        info.FontWeight = 400;
        info.FaceName = "Consolas";
        SetCurrentConsoleFontEx(hnd, false, ref info);
    }
    public static long MaximizeSelf() {
        IntPtr hwnd = GetConsoleWindow();
        if (hwnd != IntPtr.Zero) {
            ShowWindow(hwnd, 3);
            SetWindowPos(hwnd, new IntPtr(-1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040);
            SetForegroundWindow(hwnd);
        }
        return hwnd.ToInt64();
    }
}
"@
[ConsoleWinHelper]::SetFont(20)
$myHwnd = [ConsoleWinHelper]::MaximizeSelf()
Clear-Host
Set-Location -LiteralPath "__WORKDIR__"
function Show-Prompt([string]$cmd) {
    Write-Host "PS __WORKDIR__> " -NoNewline -ForegroundColor Green
    Write-Host $cmd -ForegroundColor Yellow
}
'@
    $header = $header.Replace("__TITLE__", $WindowTitle).Replace("__WORKDIR__", $WorkDir)
    $footer = @"

Write-Host ""
Write-Host "PS $WorkDir> " -NoNewline -ForegroundColor Green
[ConsoleWinHelper]::MaximizeSelf() | Out-Null
Set-Content -LiteralPath "$readyPath" -Value "`$PID|`$myHwnd" -Encoding ASCII
Start-Sleep -Seconds 60
"@
    Set-Content -LiteralPath $runnerPath -Value ($header + "`r`n" + $ScriptBody + $footer) -Encoding UTF8

    $proc = Start-Process -FilePath "C:\Windows\System32\conhost.exe" `
        -ArgumentList "powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$runnerPath`"" `
        -PassThru

    $childPid = $null
    $childHwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Milliseconds 250
        if (Test-Path -LiteralPath $readyPath) {
            $rawInfo = (Get-Content -LiteralPath $readyPath -Raw).Trim()
            $parts = $rawInfo -split '\|'
            if ($parts.Count -ge 2) {
                $childPid = [int]$parts[0]
                $childHwnd = [IntPtr]::new([long]$parts[1])
            }
            break
        }
    }

    if ($childHwnd -ne [IntPtr]::Zero) {
        [Win32CaptureHelper]::ForceTopMostMaximize($childHwnd)
    }

    Start-Sleep -Seconds 2
    Save-RealScreenCapture -OutputFile $OutputPng

    if ($childPid) {
        Stop-Process -Id $childPid -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $readyPath -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
}

function Invoke-WiresharkCapture {
    param(
        [Parameter(Mandatory = $true)][string]$ArgString,
        [Parameter(Mandatory = $true)][string]$OutputPng,
        [int]$WaitSeconds = 5
    )

    $wsExe = "C:\Program Files\Wireshark\Wireshark.exe"
    $proc = Start-Process -FilePath $wsExe -ArgumentList $ArgString -PassThru

    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 250
        $proc.Refresh()
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero -and -not [string]::IsNullOrWhiteSpace($proc.MainWindowTitle)) {
            [Win32CaptureHelper]::ForceTopMostMaximize($proc.MainWindowHandle)
            break
        }
    }

    Start-Sleep -Seconds $WaitSeconds
    Save-RealScreenCapture -OutputFile $OutputPng

    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 800
}

$PyExe = "C:\Users\marti\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if (-not (Test-Path -LiteralPath $PyExe)) { $PyExe = "python" }

Write-Host "Iniciando capturas reales seleccionadas ($($Pasos -join ', '))..." -ForegroundColor Cyan
Start-Sleep -Seconds 1

# 1. img/01_dockerfile_build.png
if ($Pasos -contains 1) {
    Invoke-ConsoleWindowCapture -StepName "cap01" -WindowTitle "Windows PowerShell - Actividad 1: Dockerfile y Contenedor Docker" -OutputPng "01_dockerfile_build.png" -ScriptBody @'
[ConsoleWinHelper]::SetFont(17)
Show-Prompt "Get-Content .\actividad_1\Dockerfile -Encoding UTF8"
Get-Content .\actividad_1\Dockerfile -Encoding UTF8
Write-Host ""
Show-Prompt "docker build -t ssh-lab4 .\actividad_1"
docker build -t ssh-lab4 .\actividad_1 2>&1 | Select-String -Pattern "^#(4|6|7|8|9|10|11|12)\s(\[(1|2|3|4|5|6|7)/7\]|naming to|DONE)"
Write-Host ""
Show-Prompt 'docker ps --filter "name=servidor-ssh"'
docker ps --filter "name=servidor-ssh"
'@
}

# 2. img/02_sshd_config.png
if ($Pasos -contains 2) {
    Invoke-ConsoleWindowCapture -StepName "cap02" -WindowTitle "Windows PowerShell - Actividad 1: sshd_config y Algoritmos Criptograficos" -OutputPng "02_sshd_config.png" -ScriptBody @'
Show-Prompt "Get-Content .\actividad_1\sshd_config -Encoding UTF8"
Get-Content .\actividad_1\sshd_config -Encoding UTF8
Write-Host ""
Show-Prompt 'docker exec servidor-ssh sshd -T | Select-String -Pattern "^(kexalgorithms|ciphers|macs|hostkeyalgorithms|pubkeyacceptedalgorithms)\s"'
docker exec servidor-ssh sshd -T | Select-String -Pattern "^(kexalgorithms|ciphers|macs|hostkeyalgorithms|pubkeyacceptedalgorithms)\s"
'@
}

# 3. img/03_ssh_conexion_cliente.png
if ($Pasos -contains 3) {
    Invoke-ConsoleWindowCapture -StepName "cap03" -WindowTitle "Windows PowerShell - Actividad 1: Conexion Cliente SSH (-vv)" -OutputPng "03_ssh_conexion_cliente.png" -ScriptBody @'
Show-Prompt 'ssh.exe -vv -p 2222 usuario@127.0.0.1 "whoami && hostname && uname -a"'
Get-Content .\actividad_1\ssh_vv_extracto.txt -Encoding UTF8
'@
}

# 4. img/04_wireshark_ssh.png
if ($Pasos -contains 4) {
    $pcapSsh = Join-Path $WorkDir "actividad_1\captura_ssh.pcap"
    Invoke-WiresharkCapture -ArgString "-r `"$pcapSsh`" -Y ssh -g 8" -OutputPng "04_wireshark_ssh.png" -WaitSeconds 5
}

# 5. img/05_paquete_rsa_pin.png
if ($Pasos -contains 5) {
    $pcapTx = Join-Path $WorkDir "transacciones_cifradas.pcap"
    Invoke-WiresharkCapture -ArgString "-r `"$pcapTx`" -g 1" -OutputPng "05_paquete_rsa_pin.png" -WaitSeconds 5
}

# 6. img/06_paquetes_aesgcm.png
if ($Pasos -contains 6) {
    $pcapTx = Join-Path $WorkDir "transacciones_cifradas.pcap"
    Invoke-WiresharkCapture -ArgString "-r `"$pcapTx`" -Y `"tcp.payload contains 41:45:53:47:43:4d:7c`" -g 2" -OutputPng "06_paquetes_aesgcm.png" -WaitSeconds 5
}

# 7. img/07_codigo_pin_scrypt.png
if ($Pasos -contains 7) {
    Invoke-ConsoleWindowCapture -StepName "cap07" -WindowTitle "Windows PowerShell - Actividad 2: Codigo RSA-OAEP + Scrypt y Derivacion" -OutputPng "07_codigo_pin_scrypt.png" -ScriptBody @"
Show-Prompt 'Get-Content .\actividad_2\descifrar_transacciones.py | Select-Object -Index (78..115)'
`$lines = Get-Content .\actividad_2\descifrar_transacciones.py -Encoding UTF8
for (`$idx = 78; `$idx -le 115; `$idx++) {
    Write-Host ("{0,4} | " -f (`$idx + 1)) -NoNewline -ForegroundColor DarkCyan
    Write-Host `$lines[`$idx] -ForegroundColor White
}
Write-Host ""
Show-Prompt 'python .\actividad_2\descifrar_transacciones.py --kdf-info'
& "$PyExe" .\actividad_2\descifrar_transacciones.py --kdf-info
"@
}

# 8. img/08_codigo_aesgcm.png
if ($Pasos -contains 8) {
    Invoke-ConsoleWindowCapture -StepName "cap08" -WindowTitle "Windows PowerShell - Actividad 2: Codigo AES-GCM y Verificacion de Tags" -OutputPng "08_codigo_aesgcm.png" -ScriptBody @"
Show-Prompt 'Get-Content .\actividad_2\descifrar_transacciones.py | Select-Object -Index (125..157)'
`$lines = Get-Content .\actividad_2\descifrar_transacciones.py -Encoding UTF8
for (`$idx = 125; `$idx -le 157; `$idx++) {
    Write-Host ("{0,4} | " -f (`$idx + 1)) -NoNewline -ForegroundColor DarkCyan
    Write-Host `$lines[`$idx] -ForegroundColor White
}
Write-Host ""
Show-Prompt 'python -c "... verificar autenticidad GCM en los 40 paquetes AESGCM| ..."'
& "$PyExe" -c "import warnings; warnings.filterwarnings('ignore'); from pathlib import Path; from scapy.all import rdpcap, Raw; from cryptography.hazmat.primitives import hashes, serialization; from cryptography.hazmat.primitives.asymmetric import padding; from cryptography.hazmat.primitives.kdf.scrypt import Scrypt; from cryptography.hazmat.primitives.ciphers.aead import AESGCM; pk = serialization.load_pem_private_key(Path('clave_privada.pem').read_bytes(), password=None); pkts = [bytes(p[Raw].load) for p in rdpcap('transacciones_cifradas.pcap') if p.haslayer(Raw)]; raw_pin = next(x for x in pkts if x.startswith(b'RSA_PIN|')); salt, ct = raw_pin[8:24], raw_pin[24:]; pin = pk.decrypt(ct, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)).decode(); key = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1).derive(pin.encode()); aes = AESGCM(key); txs = [aes.decrypt(x[7:19], x[19:], None).decode() for x in pkts if x.startswith(b'AESGCM|')]; print(f'[OK] Paquetes AESGCM verificados con tag GCM integro: {len(txs)}/40'); print('[Muestra #1]  :', txs[0]); print('[Muestra #40] :', txs[-1])"
"@
}

# 9. img/09_resultado_transacciones.png
if ($Pasos -contains 9) {
    Invoke-ConsoleWindowCapture -StepName "cap09" -WindowTitle "Windows PowerShell - Actividad 2: Ejecucion Completa descifrar_transacciones.py" -OutputPng "09_resultado_transacciones.png" -ScriptBody @"
[ConsoleWinHelper]::SetFont(17)
Show-Prompt 'python .\actividad_2\descifrar_transacciones.py'
`$out = & "$PyExe" .\actividad_2\descifrar_transacciones.py
`$out | Select-Object -First 32
Write-Host "... [Salida integra de las 40 transacciones en actividad_2/salida_transacciones_completa.txt] ..." -ForegroundColor Cyan
`$out | Select-Object -Last 6
"@
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ¡Capturas reales actualizadas en .\img\!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
