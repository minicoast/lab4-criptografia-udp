#!/usr/bin/env python3

import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore")

from scapy.all import rdpcap, Raw
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def resolver_ruta(archivo: str) -> str:
    """Resuelve rutas relativas tanto desde la raíz del proyecto como desde actividad_2/."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rutas_posibles = [
        archivo,
        os.path.join(base_dir, "..", archivo),
        os.path.join(base_dir, archivo),
    ]
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            return os.path.normpath(ruta)
    return archivo


def main():
    parser = argparse.ArgumentParser(
        description="Descifra las transacciones financieras de transacciones_cifradas.pcap"
    )
    parser.add_argument(
        "--kdf-info",
        action="store_true",
        help="Muestra parámetros intermedios (salt en hex, PIN y clave AES-256 derivada)",
    )
    args = parser.parse_args()

    ruta_pcap = resolver_ruta("transacciones_cifradas.pcap")
    ruta_privkey = resolver_ruta("clave_privada.pem")

    if not os.path.exists(ruta_pcap):
        print(f"[-] Error: Archivo de captura no encontrado: {ruta_pcap}")
        sys.exit(1)

    if not os.path.exists(ruta_privkey):
        print(f"[-] Error: Clave privada RSA no encontrada: {ruta_privkey}")
        sys.exit(1)

    # 1. Cargar clave privada RSA-2048 desde formato PEM
    with open(ruta_privkey, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    # 2. Leer paquetes de la captura de red
    paquetes = rdpcap(ruta_pcap)

    pin = None
    salt = None
    transacciones_cifradas = []

    # 3. Identificar paquete RSA_PIN| y paquetes AESGCM|
    for pkt in paquetes:
        if Raw in pkt:
            payload = pkt[Raw].load
            if payload.startswith(b"RSA_PIN|"):
                # Estructura: b"RSA_PIN|" (8 B) + salt (16 B) + criptograma RSA (256 B)
                datos_rsa = payload[len(b"RSA_PIN|") :]
                salt = datos_rsa[:16]
                rsa_ciphertext = datos_rsa[16:]

                # Recuperar el PIN de 4 dígitos usando RSA-OAEP con SHA-256
                pin_bytes = private_key.decrypt(
                    rsa_ciphertext,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                pin = pin_bytes.decode("utf-8").strip()

            elif payload.startswith(b"AESGCM|"):
                # Estructura tras b"AESGCM|": nonce (12 B) + ciphertext + tag GCM (16 B)
                transacciones_cifradas.append(payload[len(b"AESGCM|") :])

    if not pin or not salt:
        print("[-] Error: No se encontró el paquete RSA_PIN| válido en la captura.")
        sys.exit(1)

    # 4. Derivar clave AES de 256 bits (32 bytes) usando Scrypt
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    aes_key = kdf.derive(pin.encode("utf-8"))

    if args.kdf_info:
        print("[+] Parámetros extraídos y derivación de clave Scrypt:")
        print(f"    Salt (16 bytes hex)      : {salt.hex()}")
        print(f"    PIN recuperado (RSA-OAEP): {pin}")
        print(f"    Parámetros Scrypt        : n=2**14 (16384), r=8, p=1, length=32")
        print(f"    Clave AES-256 (hex)      : {aes_key.hex()}")
        return

    # 5. Inicializar primitiva AEAD AES-GCM con la clave derivada de 256 bits
    aesgcm = AESGCM(aes_key)

    # 6. Construir salida exacta según Figura 1 de la guía oficial
    lineas_salida = [
        "[+] PIN recuperado mediante RSA",
        f"[+] PIN: {pin}",
        f"[+] Transacciones cifradas encontradas: {len(transacciones_cifradas)}",
        "",
        "========== TRANSACCIONES ==========",
        "",
    ]

    for idx, bloque_aes in enumerate(transacciones_cifradas, start=1):
        nonce = bloque_aes[:12]
        ciphertext = bloque_aes[12:]

        # AESGCM.decrypt valida el Authentication Tag de 128 bits antes de retornar el texto plano
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        mensaje = plaintext_bytes.decode("utf-8")

        lineas_salida.append(f"[Transacción {idx}]")
        lineas_salida.append(mensaje)
        if idx < len(transacciones_cifradas):
            lineas_salida.append("")

    salida_final = "\n".join(lineas_salida)
    print(salida_final)

    # Guardar salida íntegra de las 40 transacciones en actividad_2/salida_transacciones_completa.txt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_salida = os.path.join(base_dir, "salida_transacciones_completa.txt")
    with open(ruta_salida, "w", encoding="utf-8") as f_out:
        f_out.write(salida_final + "\n")


if __name__ == "__main__":
    main()
