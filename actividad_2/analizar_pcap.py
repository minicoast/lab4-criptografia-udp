#!/usr/bin/env python3
"""
Laboratorio 4 - Criptografía y Seguridad en Redes
Actividad 2: Inspección y Volcado Hexadecimal/ASCII de transacciones_cifradas.pcap

Inspecciona todos los paquetes de ./transacciones_cifradas.pcap y exporta en
actividad_2/hexdump_paquetes.txt los metadatos de red, el desglose estructural
de campos criptográficos y el volcado hexadecimal/ASCII estilo Wireshark tanto
del paquete #1 (RSA_PIN|) como de los 40 paquetes (AESGCM|).
"""

import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

from scapy.all import rdpcap, Ether, IP, TCP, UDP, Raw


def resolver_ruta(archivo):
    """Permite ejecutar el script desde la raíz del proyecto o desde actividad_2/."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        archivo,
        os.path.join(base_dir, "..", archivo),
        os.path.join(base_dir, archivo),
    ]
    for ruta in candidatos:
        if os.path.exists(ruta):
            return os.path.normpath(ruta)
    return archivo


def formatear_hexdump(datos: bytes, bytes_por_linea: int = 16) -> str:
    """Genera un volcado hexadecimal y ASCII idéntico al panel de bytes de Wireshark."""
    lineas = []
    for offset in range(0, len(datos), bytes_por_linea):
        bloque = datos[offset : offset + bytes_por_linea]
        mitad_izq = " ".join(f"{b:02x}" for b in bloque[:8])
        mitad_der = " ".join(f"{b:02x}" for b in bloque[8:])
        hex_str = f"{mitad_izq:<23}  {mitad_der:<23}"
        ascii_izq = "".join(chr(b) if 32 <= b <= 126 else "." for b in bloque[:8])
        ascii_der = "".join(chr(b) if 32 <= b <= 126 else "." for b in bloque[8:])
        lineas.append(f"{offset:04x}   {hex_str}   {ascii_izq} {ascii_der}".rstrip())
    return "\n".join(lineas)


def extraer_metadatos(pkt, idx: int) -> dict:
    """Extrae direcciones IP, puertos, protocolo y marca de tiempo de una trama."""
    ts = float(pkt.time)
    fecha_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")
    src_ip = pkt[IP].src if IP in pkt else "N/A"
    dst_ip = pkt[IP].dst if IP in pkt else "N/A"
    proto = "RAW"
    sport, dport = "-", "-"
    if TCP in pkt:
        proto = "TCP"
        sport, dport = pkt[TCP].sport, pkt[TCP].dport
    elif UDP in pkt:
        proto = "UDP"
        sport, dport = pkt[UDP].sport, pkt[UDP].dport
    payload = pkt[Raw].load if Raw in pkt else b""
    return {
        "frame": idx,
        "timestamp": fecha_str,
        "frame_len": len(bytes(pkt)),
        "payload_len": len(payload),
        "src": f"{src_ip}:{sport}",
        "dst": f"{dst_ip}:{dport}",
        "proto": proto,
        "payload": payload,
    }


def main():
    ruta_pcap = resolver_ruta("transacciones_cifradas.pcap")
    if not os.path.exists(ruta_pcap):
        print(f"[-] Error: No se encontró {ruta_pcap}")
        sys.exit(1)

    paquetes = rdpcap(ruta_pcap)
    salida = []
    salida.append("=" * 82)
    salida.append("INSPECCIÓN DE CAPTURA PCAP: transacciones_cifradas.pcap")
    salida.append(f"Total de tramas en archivo: {len(paquetes)}")
    salida.append("=" * 82)

    paquetes_rsa = []
    paquetes_aes = []

    for idx, pkt in enumerate(paquetes, start=1):
        meta = extraer_metadatos(pkt, idx)
        payload = meta["payload"]
        if payload.startswith(b"RSA_PIN|"):
            paquetes_rsa.append(meta)
        elif payload.startswith(b"AESGCM|"):
            paquetes_aes.append(meta)

    salida.append(f"[+] Paquetes con etiqueta 'RSA_PIN|' identificados : {len(paquetes_rsa)}")
    salida.append(f"[+] Paquetes con etiqueta 'AESGCM|' identificados  : {len(paquetes_aes)}")
    salida.append("")

    # Resumen tabular de todos los paquetes relevantes
    salida.append("-" * 82)
    salida.append(f"{'No.':<5} {'Proto':<6} {'Origen':<21} {'Destino':<21} {'Frame':<7} {'Payload':<8} {'Etiqueta'}")
    salida.append("-" * 82)
    for m in paquetes_rsa + paquetes_aes:
        etiqueta = "RSA_PIN|" if m["payload"].startswith(b"RSA_PIN|") else "AESGCM|"
        salida.append(
            f"{m['frame']:<5} {m['proto']:<6} {m['src']:<21} {m['dst']:<21} "
            f"{m['frame_len']:<7} {m['payload_len']:<8} {etiqueta}"
        )
    salida.append("-" * 82)
    salida.append("")

    # Detalle exhaustivo del paquete #1 (RSA_PIN|)
    for m in paquetes_rsa:
        payload = m["payload"]
        header = payload[:8]
        salt = payload[8:24]
        rsa_ct = payload[24:]

        salida.append("=" * 82)
        salida.append(f"DETALLE PAQUETE #{m['frame']} - ETIQUETA RSA_PIN|")
        salida.append("=" * 82)
        salida.append(f"Timestamp      : {m['timestamp']}")
        salida.append(f"Flujo de red   : {m['src']} -> {m['dst']} ({m['proto']})")
        salida.append(f"Longitud trama : {m['frame_len']} bytes | Payload aplicación: {m['payload_len']} bytes")
        salida.append("Desglose estructural del Payload:")
        salida.append(f"  [0x0000 - 0x0007] Encabezado ASCII (8 B)     : {header.decode('ascii')} ({header.hex()})")
        salida.append(f"  [0x0008 - 0x0017] Salt para Scrypt (16 B)    : {salt.hex()}")
        salida.append(f"  [0x0018 - 0x0117] Criptograma RSA-2048 (256B): {rsa_ct[:16].hex()}...{rsa_ct[-16:].hex()}")
        salida.append("")
        salida.append("Volcado Hexadecimal / ASCII (Frame completo):")
        salida.append(formatear_hexdump(bytes(paquetes[m["frame"] - 1])))
        salida.append("")
        salida.append("Volcado Hexadecimal / ASCII (Payload de aplicación RSA_PIN|):")
        salida.append(formatear_hexdump(payload))
        salida.append("")

    # Detalle de los 40 paquetes AESGCM|
    salida.append("=" * 82)
    salida.append(f"DETALLE DE LOS {len(paquetes_aes)} PAQUETES CON ETIQUETA AESGCM|")
    salida.append("=" * 82)
    for idx_aes, m in enumerate(paquetes_aes, start=1):
        payload = m["payload"]
        header = payload[:7]
        nonce = payload[7:19]
        ct_and_tag = payload[19:]
        ct_only = ct_and_tag[:-16]
        gcm_tag = ct_and_tag[-16:]

        salida.append(f"\n--- Transacción Cifrada #{idx_aes:02d} (Frame #{m['frame']}) ---")
        salida.append(
            f"Timestamp: {m['timestamp']} | {m['src']} -> {m['dst']} ({m['proto']}) | "
            f"Frame: {m['frame_len']} B | Payload: {m['payload_len']} B"
        )
        salida.append(f"  [0x0000 - 0x0006] Encabezado (7 B)       : {header.decode('ascii')} ({header.hex()})")
        salida.append(f"  [0x0007 - 0x0012] Nonce GCM (12 B)       : {nonce.hex()}")
        salida.append(f"  [0x0013 - 0x{19 + len(ct_only) - 1:04x}] Ciphertext ({len(ct_only)} B)      : {ct_only[:16].hex()}...")
        salida.append(f"  [0x{19 + len(ct_only):04x} - 0x{len(payload) - 1:04x}] GCM Auth Tag (16 B)    : {gcm_tag.hex()}")
        salida.append("Volcado Payload Hex/ASCII:")
        salida.append(formatear_hexdump(payload))

    texto_final = "\n".join(salida) + "\n"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_out = os.path.join(base_dir, "hexdump_paquetes.txt")
    with open(ruta_out, "w", encoding="utf-8") as f:
        f.write(texto_final)

    # Imprimir resumen ejecutivo en consola para verificación y capturas
    print(f"[+] Archivo analizado: {ruta_pcap}")
    print(f"[+] Total de tramas inspeccionadas: {len(paquetes)}")
    print(f"[+] Paquete RSA_PIN| encontrado en Frame #{paquetes_rsa[0]['frame']} ({paquetes_rsa[0]['payload_len']} bytes de payload)")
    salt_hex = paquetes_rsa[0]["payload"][8:24].hex()
    print(f"    -> Header (8 B) : RSA_PIN|")
    print(f"    -> Salt  (16 B) : {salt_hex}")
    print(f"    -> RSA CT(256 B): {paquetes_rsa[0]['payload'][24:40].hex()}...")
    print(f"[+] Paquetes AESGCM| encontrados: {len(paquetes_aes)} (Frames #{paquetes_aes[0]['frame']} a #{paquetes_aes[-1]['frame']})")
    print(f"[+] Volcado completo exportado en: {ruta_out}")


if __name__ == "__main__":
    main()
