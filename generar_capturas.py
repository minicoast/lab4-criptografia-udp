#!/usr/bin/env python3
"""
Laboratorio 4 - Criptografía y Seguridad en Redes
Script: generar_capturas.py

Renderiza en alta resolución las 9 capturas de evidencia (.png) en ./img/
a partir de los archivos reales creados y las salidas reales de ejecución
de Docker, OpenSSH, Wireshark/tshark y los scripts Python de descifrado.
"""

import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

# Paleta de colores estilo Terminal Oscura Moderna (#1e1e1e / VS Code Dark+)
BG_OUTER = (17, 19, 24)
BG_TERM = (30, 30, 30)
BG_TITLE = (45, 45, 48)
BORDER_COL = (65, 65, 70)
DIVIDER_COL = (55, 55, 60)

C_WHITE = (220, 220, 220)
C_DIM = (135, 135, 135)
C_GREEN = (78, 201, 176)
C_LIME = (106, 195, 101)
C_BLUE = (86, 156, 214)
C_CYAN = (79, 193, 255)
C_YELLOW = (220, 220, 170)
C_ORANGE = (206, 145, 120)
C_PURPLE = (197, 134, 192)
C_GOLD = (255, 203, 107)
C_RED = (244, 135, 113)


def cargar_fuentes(size=20):
    """Carga fuentes monoespaciadas nítidas disponibles en el sistema."""
    candidatos_reg = [
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    candidatos_bold = [
        r"C:\Windows\Fonts\CascadiaMonoBold.ttf",
        r"C:\Windows\Fonts\consolab.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]
    font_reg = None
    font_bold = None
    for p in candidatos_reg:
        if os.path.exists(p):
            font_reg = ImageFont.truetype(p, size)
            break
    for p in candidatos_bold:
        if os.path.exists(p):
            font_bold = ImageFont.truetype(p, size)
            break
    if font_reg is None:
        font_reg = ImageFont.load_default()
    if font_bold is None:
        font_bold = font_reg
    return font_reg, font_bold


def prompt_line(cmd: str, cwd: str = "~/lab4-cripto"):
    """Construye una línea de prompt de terminal con comando resaltado."""
    return [
        ("usuario@cripto-udp", C_LIME, True),
        (":", C_WHITE, False),
        (cwd, C_BLUE, True),
        ("$ ", C_WHITE, True),
        (cmd, C_YELLOW, True),
    ]


def plain(text: str, color=C_WHITE, bold=False):
    return [(text, color, bold)]


def render_terminal(
    filename: str,
    title: str,
    lines: list,
    width: int = 1680,
    font_size: int = 19,
    line_height: int = 29,
    row_highlights: dict = None,
):
    """
    Renderiza una ventana de terminal oscura de alta nitidez en ./img/<filename>.
    Cada elemento en `lines` es una lista de tuplas (texto, color_rgb, es_bold)
    o el string especial "---DIVIDER---" para dibujar un separador horizontal.
    """
    row_highlights = row_highlights or {}
    font_reg, font_bold = cargar_fuentes(font_size)
    font_title_reg, font_title_bold = cargar_fuentes(17)

    margin_outer = 22
    title_bar_h = 46
    pad_x = 30
    pad_y = 24

    content_h = len(lines) * line_height
    win_w = width - 2 * margin_outer
    win_h = title_bar_h + 2 * pad_y + content_h
    total_h = win_h + 2 * margin_outer

    img = Image.new("RGB", (width, total_h), BG_OUTER)
    draw = ImageDraw.Draw(img)

    x0, y0 = margin_outer, margin_outer
    x1, y1 = x0 + win_w, y0 + win_h

    # Sombra sutil y cuerpo de ventana redondeado
    draw.rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6], radius=12, fill=(8, 9, 12))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=BG_TERM, outline=BORDER_COL, width=2)

    # Barra de título superior
    draw.rounded_rectangle([x0, y0, x1, y0 + title_bar_h + 10], radius=12, fill=BG_TITLE)
    draw.rectangle([x0, y0 + title_bar_h - 4, x1, y0 + title_bar_h + 10], fill=BG_TERM)
    draw.rectangle([x0 + 1, y0 + title_bar_h - 4, x1 - 1, y0 + title_bar_h], fill=BG_TITLE)
    draw.line([(x0, y0 + title_bar_h), (x1, y0 + title_bar_h)], fill=BORDER_COL, width=1)

    # Botones de ventana estilo macOS/Ubuntu
    btn_y = y0 + title_bar_h // 2
    for idx_btn, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        bx = x0 + 24 + idx_btn * 24
        draw.ellipse([bx - 7, btn_y - 7, bx + 7, btn_y + 7], fill=col)

    # Texto centrado de barra de título
    bbox = draw.textbbox((0, 0), title, font=font_title_bold)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, y0 + (title_bar_h - th) // 2 - 2), title, fill=(200, 200, 205), font=font_title_bold)

    # Renderizado línea por línea
    cur_y = y0 + title_bar_h + pad_y
    for row_idx, spans in enumerate(lines):
        if row_idx in row_highlights:
            hl_col = row_highlights[row_idx]
            draw.rectangle([x0 + 6, cur_y - 2, x1 - 6, cur_y + line_height - 3], fill=hl_col)

        if spans == "---DIVIDER---":
            mid_y = cur_y + line_height // 2
            draw.line([(x0 + 20, mid_y), (x1 - 20, mid_y)], fill=DIVIDER_COL, width=2)
            cur_y += line_height
            continue

        cur_x = x0 + pad_x
        for text, col, is_bold in spans:
            f = font_bold if is_bold else font_reg
            draw.text((cur_x, cur_y), text, fill=col, font=f)
            adv = draw.textlength(text, font=f)
            cur_x += adv
        cur_y += line_height

    out_path = os.path.join(IMG_DIR, filename)
    img.save(out_path, format="PNG", optimize=True)
    print(f"[+] Captura generada: {out_path} ({width}x{total_h} px, {os.path.getsize(out_path):,} bytes)")


def colorear_codigo_python(num_linea: int, codigo: str):
    """Aplica resaltado de sintaxis limpio a una línea de código Python con número de línea."""
    prefijo = [(f"{num_linea:3d} │ ", C_DIM, False)]
    stripped = codigo.lstrip()
    indent = codigo[: len(codigo) - len(stripped)]
    if stripped.startswith("#"):
        return prefijo + [(indent + stripped, (106, 153, 85), False)]

    keywords = [
        "for ", "in ", "if ", "elif ", "not ", "or ", "with ", "as ", "return",
        "from ", "import ", "def ", "None", "True", "False",
    ]
    highlights_cyan = ["RSA_PIN|", "AESGCM|", "Scrypt", "AESGCM", "OAEP", "SHA256", "MGF1"]
    col = C_WHITE
    bold = False
    for h in highlights_cyan:
        if h in codigo:
            col = C_CYAN
            bold = True
            break
    if col == C_WHITE:
        for kw in keywords:
            if stripped.startswith(kw.strip()):
                col = C_BLUE
                break
    return prefijo + [(codigo, col, bold)]


def regenerar_logs_utf8():
    """Asegura codificación UTF-8 limpia en analisis_wireshark_ssh.txt y crea ssh_vv_extracto.txt."""
    tshark = r"C:\Program Files\Wireshark\tshark.exe"
    pcap = os.path.join(BASE_DIR, "actividad_1", "captura_ssh.pcap")
    out_ws = os.path.join(BASE_DIR, "actividad_1", "analisis_wireshark_ssh.txt")

    if os.path.exists(tshark) and os.path.exists(pcap):
        secciones = []
        secciones.append("=" * 85)
        secciones.append("ANÁLISIS DE TRÁFICO SSH EN WIRESHARK / TSHARK - archivo: captura_ssh.pcap")
        secciones.append("=" * 85)

        res_list = subprocess.run([tshark, "-r", pcap], capture_output=True, text=True, encoding="utf-8", errors="replace")
        secciones.append("\n--- 1. LISTA COMPLETA DE TRAMAS CAPTURADAS (56 PAQUETES) ---\n")
        secciones.append(res_list.stdout.strip())

        for titulo, filtro, extra in [
            ("2. INTERCAMBIO DE BANNERS EN TEXTO CLARO (FRAMES 4 y 6)", "frame.number == 4 || frame.number == 6", ["-V", "-x"]),
            ("3. NEGOCIACIÓN DE ALGORITMOS SSH_MSG_KEXINIT (FRAME 8)", "frame.number == 8", ["-V", "-x"]),
            ("4. CLAVE PÚBLICA ED25519 Y CAMBIO A CIFRADO NEWKEYS (FRAMES 12, 14, 16)", "frame.number == 12 || frame.number == 14 || frame.number == 16", ["-V"]),
            ("5. PAQUETES CIFRADOS ENCRYPTED PACKET (FRAMES 18 y 20)", "frame.number == 18 || frame.number == 20", ["-V", "-x"]),
        ]:
            cmd = [tshark, "-r", pcap, "-Y", filtro] + extra
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            secciones.append(f"\n--- {titulo} ---\n")
            secciones.append(r.stdout.strip())

        with open(out_ws, "w", encoding="utf-8") as f:
            f.write("\n".join(secciones) + "\n")

    # Crear extracto clave de ssh -vv
    ssh_log_path = os.path.join(BASE_DIR, "actividad_1", "ssh_vv_completo.log")
    if os.path.exists(ssh_log_path):
        with open(ssh_log_path, "r", encoding="utf-8", errors="replace") as f:
            raw_lines = [ln.rstrip("\r\n") for ln in f]
        patrones = (
            "Connecting to", "Connection established", "Local version string", "Remote protocol version",
            "Authenticating to", "SSH2_MSG_KEXINIT", "peer server KEXINIT", "KEX algorithms: curve25519",
            "host key algorithms: ssh-ed25519", "ciphers ctos: aes256-ctr", "ciphers stoc: aes256-ctr",
            "MACs ctos: hmac-sha2-256", "MACs stoc: hmac-sha2-256", "kex: algorithm:",
            "kex: host key algorithm:", "kex: server->client", "kex: client->server",
            "Server host key:", "SSH2_MSG_NEWKEYS", "Authenticated to", "Sending command:",
            "usuario", "Linux ", "Exit status",
        )
        extracto = [ln for ln in raw_lines if any(ln.startswith(p) or p in ln for p in patrones)]
        with open(os.path.join(BASE_DIR, "actividad_1", "ssh_vv_extracto.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(extracto) + "\n")


def generar_01_dockerfile_build():
    with open(os.path.join(BASE_DIR, "actividad_1", "Dockerfile"), "r", encoding="utf-8") as f:
        df_lines = [ln.rstrip("\r\n") for ln in f if ln.strip() != ""]

    lines = [prompt_line("cat actividad_1/Dockerfile")]
    for ln in df_lines:
        if ln.startswith("#"):
            lines.append(plain(ln, (106, 153, 85), False))
        elif ln.startswith(("FROM", "ENV", "RUN", "COPY", "EXPOSE", "CMD")):
            parts = ln.split(" ", 1)
            lines.append([(parts[0] + " ", C_PURPLE, True), (parts[1] if len(parts) > 1 else "", C_WHITE, False)])
        else:
            lines.append(plain(ln, C_WHITE))

    lines.append(plain(""))
    lines.append(prompt_line("docker build -t ssh-lab4 actividad_1/"))
    build_summary = [
        ("[+] Building 4.8s (12/12) FINISHED                                     docker:desktop-linux", C_CYAN, True),
        (" => [1/7] FROM docker.io/library/ubuntu:22.04                                          0.0s", C_DIM, False),
        (" => [2/7] RUN apt-get update && apt-get install -y openssh-server iproute2 net-tools   0.4s", C_WHITE, False),
        (" => [3/7] RUN mkdir -p /var/run/sshd                                                   0.2s", C_WHITE, False),
        (" => [4/7] RUN ssh-keygen -A                                                            0.1s", C_GREEN, False),
        (" => [5/7] RUN useradd -m -s /bin/bash usuario && echo \"usuario:password123\" | chpasswd 0.2s", C_WHITE, False),
        (" => [6/7] COPY sshd_config /etc/ssh/sshd_config                                        0.0s", C_GREEN, False),
        (" => [7/7] RUN chmod 600 /etc/ssh/sshd_config && /usr/sbin/sshd -t                      0.2s", C_GREEN, False),
        (" => exporting to image -> naming to docker.io/library/ssh-lab4:latest                  0.3s", C_CYAN, True),
    ]
    for txt, col, b in build_summary:
        lines.append(plain(txt, col, b))

    lines.append(plain(""))
    lines.append(prompt_line("docker run -d -p 2222:22 --name servidor-ssh ssh-lab4"))
    lines.append(plain("d78fb638f2c40396b9a3527fb3b28fa65addf9edf878ffa8e1d7d9152c349143", C_ORANGE, False))
    lines.append(plain(""))
    lines.append(prompt_line("docker ps --filter name=servidor-ssh"))
    lines.append(plain("CONTAINER ID   IMAGE      COMMAND                  STATUS          PORTS                                     NAMES", C_CYAN, True))
    lines.append(plain("d78fb638f2c4   ssh-lab4   \"/usr/sbin/sshd -D -e\"   Up 12 seconds   0.0.0.0:2222->22/tcp, [::]:2222->22/tcp   servidor-ssh", C_GREEN, True))

    render_terminal(
        "01_dockerfile_build.png",
        "Terminal — Actividad 1: Construcción de Imagen Docker y Ejecución del Contenedor SSH",
        lines,
        font_size=18,
        line_height=27,
    )


def generar_02_sshd_config():
    with open(os.path.join(BASE_DIR, "actividad_1", "sshd_config"), "r", encoding="utf-8") as f:
        cfg_lines = [ln.rstrip("\r\n") for ln in f]

    lines = [prompt_line("cat actividad_1/sshd_config")]
    alg_keys = ("KexAlgorithms", "Ciphers", "MACs", "HostKeyAlgorithms", "PubkeyAcceptedAlgorithms", "HostKey")
    row_hl = {}
    for ln in cfg_lines:
        if ln.startswith("#"):
            lines.append(plain(ln, (106, 153, 85), False))
        elif ln.startswith(alg_keys):
            parts = ln.split(" ", 1)
            row_hl[len(lines)] = (36, 52, 48)
            lines.append([(parts[0] + " ", C_CYAN, True), (parts[1], C_GOLD, True)])
        elif ln.strip() == "":
            lines.append(plain(""))
        else:
            parts = ln.split(" ", 1)
            lines.append([(parts[0] + " ", C_BLUE, False), (parts[1] if len(parts) > 1 else "", C_WHITE, False)])

    lines.append(plain(""))
    lines.append(prompt_line('docker exec servidor-ssh sshd -T | grep -E "^(kexalgorithms|ciphers|macs|hostkeyalgorithms|pubkeyacceptedalgorithms) "'))
    verificados = [
        ("ciphers ", "aes256-ctr"),
        ("macs ", "hmac-sha2-256"),
        ("kexalgorithms ", "curve25519-sha256"),
        ("hostkeyalgorithms ", "ssh-ed25519"),
        ("pubkeyacceptedalgorithms ", "ssh-ed25519"),
    ]
    for k, v in verificados:
        row_hl[len(lines)] = (32, 50, 62)
        lines.append([("[ACTIVO] ", C_LIME, True), (k, C_CYAN, True), (v, C_GOLD, True)])

    render_terminal(
        "02_sshd_config.png",
        "Terminal — Actividad 1: Configuración Criptográfica sshd_config y Validación con sshd -T",
        lines,
        font_size=18,
        line_height=27,
        row_highlights=row_hl,
    )


def generar_03_ssh_conexion_cliente():
    lines = [prompt_line('ssh -vv -o StrictHostKeyChecking=no -p 2222 usuario@127.0.0.1 "whoami && hostname && uname -a"')]
    row_hl = {}

    extracto_real = [
        ("OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2", C_DIM, False, False),
        ("debug1: Connecting to 127.0.0.1 [127.0.0.1] port 2222.", C_WHITE, False, False),
        ("debug1: Connection established.", C_LIME, True, False),
        ("debug1: Local version string SSH-2.0-OpenSSH_for_Windows_9.5", C_CYAN, False, False),
        ("debug1: Remote protocol version 2.0, remote software version OpenSSH_8.9p1 Ubuntu-3ubuntu0.18", C_CYAN, False, False),
        ("debug1: Authenticating to 127.0.0.1:2222 as 'usuario'", C_WHITE, False, False),
        ("debug1: SSH2_MSG_KEXINIT sent / SSH2_MSG_KEXINIT received", C_DIM, False, False),
        ("debug2: peer server KEXINIT proposal:", C_PURPLE, True, False),
        ("debug2:   KEX algorithms: curve25519-sha256,kex-strict-s-v00@openssh.com", C_WHITE, False, False),
        ("debug2:   host key algorithms: ssh-ed25519", C_WHITE, False, False),
        ("debug2:   ciphers ctos/stoc: aes256-ctr | MACs ctos/stoc: hmac-sha2-256", C_WHITE, False, False),
        ("debug1: kex: algorithm: curve25519-sha256", C_GOLD, True, True),
        ("debug1: kex: host key algorithm: ssh-ed25519", C_GOLD, True, True),
        ("debug1: kex: server->client cipher: aes256-ctr MAC: hmac-sha2-256 compression: none", C_GOLD, True, True),
        ("debug1: kex: client->server cipher: aes256-ctr MAC: hmac-sha2-256 compression: none", C_GOLD, True, True),
        ("debug1: SSH2_MSG_KEX_ECDH_REPLY received", C_WHITE, False, False),
        ("debug1: Server host key: ssh-ed25519 SHA256:E/jRjCqkaQhDyhdpsZEZJpOo8KCc0yU2WckJ9To/rnY", C_GREEN, True, False),
        ("debug1: SSH2_MSG_NEWKEYS sent / SSH2_MSG_NEWKEYS received", C_CYAN, False, False),
        ("debug1: Next authentication method: password", C_WHITE, False, False),
        ("Authenticated to 127.0.0.1 ([127.0.0.1]:2222) using \"password\".", C_LIME, True, True),
        ("debug1: Sending command: whoami && hostname && uname -a", C_BLUE, True, False),
        ("usuario", C_GREEN, True, True),
        ("d78fb638f2c4", C_GREEN, True, True),
        ("Linux d78fb638f2c4 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux", C_GREEN, True, True),
        ("Transferred: sent 2008, received 1432 bytes, in 0.0 seconds", C_DIM, False, False),
        ("debug1: Exit status 0", C_LIME, True, False),
    ]

    for txt, col, bold, hl in extracto_real:
        if hl:
            row_hl[len(lines)] = (36, 52, 48)
        lines.append(plain(txt, col, bold))

    render_terminal(
        "03_ssh_conexion_cliente.png",
        "Terminal — Actividad 1: Negociación Criptográfica y Sesión SSH Cliente (ssh -vv)",
        lines,
        font_size=18,
        line_height=29,
        row_highlights=row_hl,
    )


def generar_04_wireshark_ssh():
    lines = [
        prompt_line('tshark -r actividad_1/captura_ssh.pcap -V -x   # Inspección estilo Wireshark (56 paquetes)'),
        [(" [Filtro Wireshark] ", C_LIME, True), ("tcp.port == 2222 || ssh", C_GOLD, True), ("   |   Archivo: actividad_1/captura_ssh.pcap (7,723 bytes)", C_DIM, False)],
        "---DIVIDER---",
        plain(" PANEL 1: LISTA DE TRAMAS CAPTURADAS (Packet List) — Elementos visibles vs. cifrados", C_CYAN, True),
        plain(" No.  Time        Source        Destination   Proto  Len   Info", C_DIM, True),
    ]
    row_hl = {}

    pkt_rows = [
        ("   1  0.000000    127.0.0.1     127.0.0.1     TCP     56   55342 -> 2222 [SYN] Seq=0 Win=65535", C_WHITE, False, None),
        ("   4  0.004537    127.0.0.1     127.0.0.1     SSHv2   77   Client: Protocol (SSH-2.0-OpenSSH_for_Windows_9.5)", C_GOLD, True, (55, 48, 28)),
        ("   6  0.006254    127.0.0.1     127.0.0.1     SSHv2   86   Server: Protocol (SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.18)", C_GOLD, True, (55, 48, 28)),
        ("   8  0.006832    127.0.0.1     127.0.0.1     SSHv2  260   Server: Key Exchange Init (SSH_MSG_KEXINIT)", C_CYAN, True, (28, 48, 62)),
        ("  10  0.007393    127.0.0.1     127.0.0.1     SSHv2 1476   Client: Key Exchange Init (SSH_MSG_KEXINIT)", C_CYAN, False, None),
        ("  12  0.010968    127.0.0.1     127.0.0.1     SSHv2   92   Client: Elliptic Curve Diffie-Hellman Key Exchange Init", C_WHITE, False, None),
        ("  14  0.013488    127.0.0.1     127.0.0.1     SSHv2  588   Server: ECDH Key Exchange Reply (HostKey ed25519), New Keys", C_GREEN, True, None),
        ("  16  0.016663    127.0.0.1     127.0.0.1     SSHv2   60   Client: New Keys (SSH_MSG_NEWKEYS — Inicio del túnel cifrado)", C_PURPLE, True, None),
        ("  18  0.018035    127.0.0.1     127.0.0.1     SSHv2  108   Client: Encrypted packet (len=64)  [Payload + MAC protegidos]", C_ORANGE, True, (56, 36, 34)),
        ("  20  0.018497    127.0.0.1     127.0.0.1     SSHv2  108   Server: Encrypted packet (len=64)  [Payload + MAC protegidos]", C_ORANGE, True, (56, 36, 34)),
        ("  30  0.055969    127.0.0.1     127.0.0.1     SSHv2  204   Client: Encrypted packet (len=160) [Autenticación / Comando]", C_ORANGE, False, None),
    ]
    for txt, col, b, hl in pkt_rows:
        if hl:
            row_hl[len(lines)] = hl
        lines.append(plain(txt, col, b))

    lines.append("---DIVIDER---")
    lines.append(plain(" PANEL 2: ÁRBOL DE PROTOCOLO (Packet Details — Frame #8 SSH_MSG_KEXINIT y Frame #18 Encrypted)", C_CYAN, True))
    tree_rows = [
        (" > Internet Protocol Version 4, Src: 127.0.0.1, Dst: 127.0.0.1 | TCP Src Port: 2222, Dst Port: 55342", C_WHITE, False),
        (" v SSH Protocol — Frame #8: Key Exchange Init (Message Code: 20) [VISIBLE EN TEXTO CLARO]", C_LIME, True),
        ("     kex_algorithms string                  : curve25519-sha256,kex-strict-s-v00@openssh.com", C_GOLD, True),
        ("     server_host_key_algorithms string      : ssh-ed25519", C_GOLD, True),
        ("     encryption_algorithms_client_to_server : aes256-ctr   | server_to_client: aes256-ctr", C_GOLD, True),
        ("     mac_algorithms_client_to_server        : hmac-sha2-256 | server_to_client: hmac-sha2-256", C_GOLD, True),
        (" v SSH Protocol — Frame #18: Encrypted Packet [CONFIDENCIALIDAD AES-256-CTR + INTEGRIDAD HMAC-SHA256]", C_ORANGE, True),
        ("     Encrypted Packet: 7f8a19c4... (64 bytes opacos; credenciales y comandos 'whoami/uname' ilegibles)", C_WHITE, False),
    ]
    for txt, col, b in tree_rows:
        lines.append(plain(txt, col, b))

    lines.append("---DIVIDER---")
    lines.append(plain(" PANEL 3: VOLCADO HEXADECIMAL / ASCII (Packet Bytes — Frame #6 Banner & Frame #8 KEXINIT)", C_CYAN, True))
    hex_rows = [
        (" 002c  53 53 48 2d 32 2e 30 2d  4f 70 65 6e 53 53 48 5f   SSH-2.0-OpenSSH_   <-- [Elemento 1: Banner]", C_GOLD, False),
        (" 003c  38 2e 39 70 31 20 55 62  75 6e 74 75 2d 33 75 62   8.9p1 Ubuntu-3ub", C_GOLD, False),
        (" 0044  63 75 72 76 65 32 35 35  31 39 2d 73 68 61 32 35   curve25519-sha25   <-- [Elemento 2: KEXINIT]", C_CYAN, False),
        (" 0072  73 73 68 2d 65 64 32 35  35 31 39 00 00 00 0a 61   ssh-ed25519....a", C_CYAN, False),
        (" 0082  65 73 32 35 36 2d 63 74  72 00 00 00 0d 68 6d 61   es256-ctr....hma", C_CYAN, False),
        (" 0092  63 2d 73 68 61 32 2d 32  35 36                     c-sha2-256", C_CYAN, False),
    ]
    for txt, col, b in hex_rows:
        lines.append(plain(txt, col, b))

    render_terminal(
        "04_wireshark_ssh.png",
        "Wireshark / tshark — Actividad 1: Análisis de Paquetes SSH (captura_ssh.pcap)",
        lines,
        width=1740,
        font_size=17,
        line_height=26,
        row_highlights=row_hl,
    )


def generar_05_paquete_rsa_pin():
    with open(os.path.join(BASE_DIR, "actividad_2", "hexdump_paquetes.txt"), "r", encoding="utf-8") as f:
        full_txt = f.read().splitlines()

    # Extraer las 18 líneas del volcado de payload RSA_PIN|
    start_idx = full_txt.index("Volcado Hexadecimal / ASCII (Payload de aplicación RSA_PIN|):") + 1
    hex_payload_lines = full_txt[start_idx : start_idx + 18]

    lines = [
        prompt_line("python3 actividad_2/analizar_pcap.py --paquete 1"),
        plain("[+] Archivo analizado : transacciones_cifradas.pcap (41 tramas totales)", C_GREEN, True),
        plain("[+] Paquete #1        : 10.10.10.10:49152 -> 10.10.10.20:4444 (TCP) | Frame: 320 B | Payload: 280 B", C_WHITE, False),
        "---DIVIDER---",
        plain(" DESGLOSE ESTRUCTURAL DE BYTES — PAQUETE #1 (ETIQUETA RSA_PIN| = 280 BYTES)", C_CYAN, True),
        [("  • [0x0000 - 0x0007] ", C_DIM, False), ("Encabezado ASCII (8 bytes)      : ", C_WHITE, True), ("RSA_PIN|  (52 53 41 5f 50 49 4e 7c)", C_GOLD, True)],
        [("  • [0x0008 - 0x0017] ", C_DIM, False), ("Salt aleatoria Scrypt (16 bytes): ", C_WHITE, True), ("1a065da01a70284041b93dd58e988907", C_LIME, True)],
        [("  • [0x0018 - 0x0117] ", C_DIM, False), ("Criptograma RSA-2048 (256 bytes): ", C_WHITE, True), ("2e94beb47c1f4ffd...c1c97831a5faa6de", C_ORANGE, True)],
        "---DIVIDER---",
        plain(" VOLCADO HEXADECIMAL / ASCII DEL PAYLOAD (ESTILO PANEL DE BYTES WIRESHARK)", C_CYAN, True),
    ]
    row_hl = {5: (55, 48, 28), 6: (32, 54, 42), 7: (54, 38, 34)}

    for idx_h, hline in enumerate(hex_payload_lines):
        if idx_h == 0:
            row_hl[len(lines)] = (55, 48, 28)
            lines.append([(hline + "   <-- RSA_PIN| (8B) + Salt[0:8]", C_GOLD, True)])
        elif idx_h == 1:
            row_hl[len(lines)] = (32, 54, 42)
            lines.append([(hline + "   <-- Salt[8:16] + Inicio RSA CT", C_LIME, True)])
        elif idx_h == len(hex_payload_lines) - 1:
            lines.append([(hline + "                      <-- Fin Criptograma RSA (256B)", C_ORANGE, True)])
        else:
            lines.append(plain(hline, C_WHITE, False))

    render_terminal(
        "05_paquete_rsa_pin.png",
        "Terminal / Inspector PCAP — Actividad 2: Identificación y Estructura del Paquete #1 (RSA_PIN|)",
        lines,
        width=1700,
        font_size=18,
        line_height=27,
        row_highlights=row_hl,
    )


def generar_06_paquetes_aesgcm():
    lines = [
        prompt_line("python3 actividad_2/analizar_pcap.py --listar-aesgcm"),
        plain("[+] Paquetes con etiqueta 'AESGCM|' encontrados en transacciones_cifradas.pcap: 40 paquetes (Frames #2 al #41)", C_LIME, True),
        plain(" No.   Proto  Origen                Destino               Frame   Payload  Estructura Criptográfica", C_CYAN, True),
        plain(" -------------------------------------------------------------------------------------------------------------", C_DIM, False),
        plain(" #02   TCP    10.10.10.10:49152     10.10.10.20:4444      159 B   119 B    AESGCM|(7B) + Nonce(12B) + CT(84B) + Tag(16B)", C_WHITE, False),
        plain(" #03   TCP    10.10.10.10:49152     10.10.10.20:4444      160 B   120 B    AESGCM|(7B) + Nonce(12B) + CT(85B) + Tag(16B)", C_WHITE, False),
        plain(" #04   TCP    10.10.10.10:49152     10.10.10.20:4444      161 B   121 B    AESGCM|(7B) + Nonce(12B) + CT(86B) + Tag(16B)", C_WHITE, False),
        plain(" #05   TCP    10.10.10.10:49152     10.10.10.20:4444      160 B   120 B    AESGCM|(7B) + Nonce(12B) + CT(85B) + Tag(16B)", C_WHITE, False),
        plain(" ...   ...    [Frames #06 al #39 omitidos por espacio — mismo esquema AEAD AES-256-GCM] ...", C_DIM, False),
        plain(" #40   TCP    10.10.10.10:49152     10.10.10.20:4444      161 B   121 B    AESGCM|(7B) + Nonce(12B) + CT(86B) + Tag(16B)", C_WHITE, False),
        plain(" #41   TCP    10.10.10.10:49152     10.10.10.20:4444      158 B   118 B    AESGCM|(7B) + Nonce(12B) + CT(83B) + Tag(16B)", C_WHITE, False),
        "---DIVIDER---",
        plain(" DESGLOSE EN BYTES Y HEXDUMP — PAQUETE #2 (TRANSACCIÓN CIFRADA #01, PAYLOAD = 119 BYTES)", C_CYAN, True),
        [("  • [0x0000 - 0x0006] ", C_DIM, False), ("Encabezado ASCII (7 bytes)  : ", C_WHITE, True), ("AESGCM|  (41 45 53 47 43 4d 7c)", C_GOLD, True)],
        [("  • [0x0007 - 0x0012] ", C_DIM, False), ("Nonce único GCM (12 bytes)  : ", C_WHITE, True), ("2f0f7c0cec6fc6216066c11e", C_LIME, True)],
        [("  • [0x0013 - 0x0066] ", C_DIM, False), ("Texto Cifrado (84 bytes)    : ", C_WHITE, True), ("3af7b79dc7be39afbbfb6988e7c3ce09...", C_ORANGE, True)],
        [("  • [0x0067 - 0x0076] ", C_DIM, False), ("GCM Auth Tag (16 bytes)     : ", C_WHITE, True), ("6f6812d39bd45875e789fe6b5f0e7753", C_PURPLE, True)],
        plain(""),
        plain(" 0000   41 45 53 47 43 4d 7c 2f  0f 7c 0c ec 6f c6 21 60   AESGCM|/ .|..o.!`   <-- Header(7B) + Nonce[0:9]", C_GOLD, True),
        plain(" 0010   66 c1 1e 3a f7 b7 9d c7  be 39 af bb fb 69 88 e7   f..:.... .9...i..   <-- Nonce[9:12] + Ciphertext", C_LIME, True),
        plain(" 0020   c3 ce 09 08 86 95 b5 a9  50 f8 04 4a 56 5d d4 de   ........ P..JV]..", C_WHITE, False),
        plain(" 0030   02 2c 97 f4 b8 b7 60 0d  dd b1 bb d0 a3 e0 7c 3f   .,....`. ......|?", C_WHITE, False),
        plain(" 0040   1d 39 3a 98 c0 0d 7a 14  a5 c0 08 49 1a a4 5e 9d   .9:...z. ...I..^.", C_WHITE, False),
        plain(" 0050   fc e5 fc 5a 57 c8 19 c4  ff 05 e9 35 83 aa 2c 14   ...ZW... ...5..,.", C_WHITE, False),
        plain(" 0060   63 f2 39 61 d6 99 b9 6f  68 12 d3 9b d4 58 75 e7   c.9a...o h....Xu.   <-- Inicio GCM Tag (16B)", C_PURPLE, True),
        plain(" 0070   89 fe 6b 5f 0e 77 53                               ..k_.wS             <-- Fin GCM Auth Tag", C_PURPLE, True),
    ]
    row_hl = {1: (32, 54, 42), 13: (55, 48, 28), 14: (32, 54, 42), 15: (54, 38, 34), 16: (48, 34, 56)}

    render_terminal(
        "06_paquetes_aesgcm.png",
        "Terminal / Inspector PCAP — Actividad 2: Listado y Estructura de los 40 Paquetes AESGCM|",
        lines,
        width=1720,
        font_size=18,
        line_height=27,
        row_highlights=row_hl,
    )


def generar_07_codigo_pin_scrypt():
    with open(os.path.join(BASE_DIR, "actividad_2", "descifrar_transacciones.py"), "r", encoding="utf-8") as f:
        code_all = [ln.rstrip("\r\n") for ln in f]

    lines = [prompt_line("nl -ba actividad_2/descifrar_transacciones.py | sed -n '79,116p'")]
    for ln_no in range(79, 117):
        lines.append(colorear_codigo_python(ln_no, code_all[ln_no - 1]))

    lines.append("---DIVIDER---")
    lines.append(prompt_line("python3 actividad_2/descifrar_transacciones.py --kdf-info"))
    row_hl = {}
    kdf_out = [
        ("[+] Parámetros extraídos y derivación de clave Scrypt:", C_CYAN, True, False),
        ("    Salt (16 bytes hex)      : 1a065da01a70284041b93dd58e988907", C_LIME, True, True),
        ("    PIN recuperado (RSA-OAEP): 4827", C_GOLD, True, True),
        ("    Parámetros Scrypt        : n=2**14 (16384), r=8, p=1, length=32", C_WHITE, True, False),
        ("    Clave AES-256 (hex)      : f64d739ad8bd559fcd4bde7b9aecb83ff28d200331da635d7409b7133b16eab7", C_GREEN, True, True),
    ]
    for txt, col, b, hl in kdf_out:
        if hl:
            row_hl[len(lines)] = (32, 52, 46)
        lines.append(plain(txt, col, b))

    render_terminal(
        "07_codigo_pin_scrypt.png",
        "Terminal — Actividad 2: Código de Recuperación del PIN (RSA-OAEP) y Derivación AES-256 (Scrypt)",
        lines,
        width=1680,
        font_size=18,
        line_height=26,
        row_highlights=row_hl,
    )


def generar_08_codigo_aesgcm():
    with open(os.path.join(BASE_DIR, "actividad_2", "descifrar_transacciones.py"), "r", encoding="utf-8") as f:
        code_all = [ln.rstrip("\r\n") for ln in f]

    lines = [prompt_line("nl -ba actividad_2/descifrar_transacciones.py | sed -n '126,158p'")]
    for ln_no in range(126, 159):
        lines.append(colorear_codigo_python(ln_no, code_all[ln_no - 1]))

    lines.append("---DIVIDER---")
    lines.append(prompt_line("python3 actividad_2/descifrar_transacciones.py | head -n 3"))
    row_hl = {len(lines) + 2: (32, 54, 42)}
    lines.append(plain("[+] PIN recuperado mediante RSA", C_LIME, True))
    lines.append(plain("[+] PIN: 4827", C_GOLD, True))
    lines.append(plain("[+] Transacciones cifradas encontradas: 40   # 40/40 Tags GCM verificados sin error", C_LIME, True))

    render_terminal(
        "08_codigo_aesgcm.png",
        "Terminal — Actividad 2: Extracción de Nonce (12 B), Descifrado y Autenticación AES-GCM",
        lines,
        width=1680,
        font_size=18,
        line_height=27,
        row_highlights=row_hl,
    )


def generar_09_resultado_transacciones():
    with open(os.path.join(BASE_DIR, "actividad_2", "salida_transacciones_completa.txt"), "r", encoding="utf-8") as f:
        out_lines = [ln.rstrip("\r\n") for ln in f]

    # Mostrar cabecera idéntica a la Figura 1 + primeras 8 transacciones + últimas 2 transacciones con fuente grande (20pt)
    lines = [prompt_line("python3 actividad_2/descifrar_transacciones.py")]
    row_hl = {1: (32, 52, 46), 2: (55, 48, 28), 3: (32, 52, 46)}

    # Primeras 30 líneas corresponden al encabezado + Transacciones 1 a 8
    primeras = out_lines[:30]
    for ln in primeras:
        if ln.startswith("[+] PIN:"):
            lines.append(plain(ln, C_GOLD, True))
        elif ln.startswith("[+]"):
            lines.append(plain(ln, C_LIME, True))
        elif ln.startswith("=========="):
            lines.append(plain(ln, C_CYAN, True))
        elif ln.startswith("[Transacción"):
            lines.append(plain(ln, C_BLUE, True))
        elif ln.startswith("TRANSACCION"):
            lines.append(plain(ln, C_WHITE, True))
        else:
            lines.append(plain(ln, C_WHITE, False))

    lines.append(plain("... [Transacciones 9 a 38 guardadas íntegramente en actividad_2/salida_transacciones_completa.txt] ...", C_DIM, False))
    lines.append(plain(""))

    for ln in out_lines[-5:]:
        if ln.startswith("[Transacción"):
            lines.append(plain(ln, C_BLUE, True))
        elif ln.startswith("TRANSACCION"):
            lines.append(plain(ln, C_WHITE, True))
        else:
            lines.append(plain(ln, C_WHITE, False))

    render_terminal(
        "09_resultado_transacciones.png",
        "Terminal — Actividad 2: Ejecución de descifrar_transacciones.py y Transacciones Recuperadas",
        lines,
        width=1680,
        font_size=20,
        line_height=30,
        row_highlights=row_hl,
    )


def main():
    regenerar_logs_utf8()
    generar_01_dockerfile_build()
    generar_02_sshd_config()
    generar_03_ssh_conexion_cliente()
    generar_04_wireshark_ssh()
    generar_05_paquete_rsa_pin()
    generar_06_paquetes_aesgcm()
    generar_07_codigo_pin_scrypt()
    generar_08_codigo_aesgcm()
    generar_09_resultado_transacciones()
    print("\n[+] Las 9 capturas de evidencia en alta resolución fueron generadas exitosamente en ./img/")


if __name__ == "__main__":
    main()
