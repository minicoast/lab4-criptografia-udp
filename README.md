# Laboratorio 4 — Criptografía y Seguridad en Redes (2026)

Repositorio de evidencias, código fuente, capturas de tráfico (`.pcap`), configuración de servidor SSH en Docker, claves criptográficas y resultados del Laboratorio 4 de Criptografía y Seguridad en Redes (Universidad Diego Portales).

---

## Estructura del Repositorio

### Raíz — Documentación, Captura Original y Claves RSA
- [`informe_lab4.pdf`](./informe_lab4.pdf): Informe técnico final en PDF formateado según la pauta institucional.
- [`informe_lab4.tex`](./informe_lab4.tex): Código fuente del informe en LaTeX.
- [`transacciones_cifradas.pcap`](./transacciones_cifradas.pcap): Captura de red original con 1 trama `RSA_PIN|` y 40 tramas `AESGCM|`.
- [`clave_publica.pem`](./clave_publica.pem): Clave pública RSA-2048 proporcionada.
- [`clave_privada.pem`](./clave_privada.pem): Clave privada RSA-2048 utilizada para el descifrado RSA-OAEP (SHA-256).

### Actividad 1 — Servidor OpenSSH en Docker y Análisis de Tráfico (`actividad_1/`)
- [`actividad_1/Dockerfile`](./actividad_1/Dockerfile): Construcción de imagen `ssh-lab4` sobre Ubuntu 22.04 con OpenSSH Server, generación de claves de host y validación `sshd -t`.
- [`actividad_1/sshd_config`](./actividad_1/sshd_config): Configuración estricta de suites criptográficas:
  - `KexAlgorithms curve25519-sha256`
  - `Ciphers aes256-ctr`
  - `MACs hmac-sha2-256`
  - `HostKeyAlgorithms ssh-ed25519` y `PubkeyAcceptedAlgorithms ssh-ed25519`
- [`actividad_1/captura_ssh.pcap`](./actividad_1/captura_ssh.pcap): Captura de tráfico de la sesión SSH en puerto TCP 2222 (56 tramas en loopback).
- [`actividad_1/ssh_vv_completo.log`](./actividad_1/ssh_vv_completo.log): Registro interactivo del cliente `ssh -vv` negociando los 4 algoritmos y ejecutando comandos remotos.
- [`actividad_1/ssh_vv_extracto.txt`](./actividad_1/ssh_vv_extracto.txt): Extracto de líneas críticas de negociación criptográfica (`kex`, `cipher`, `MAC`, `host key`).
- [`actividad_1/analisis_wireshark_ssh.txt`](./actividad_1/analisis_wireshark_ssh.txt): Desglose de tramas, árbol de protocolo y volcado hexadecimal generado con Wireshark y `tshark`.
- [`actividad_1/docker_build_log.txt`](./actividad_1/docker_build_log.txt): Bitácora de construcción y validación del contenedor en tiempo de ejecución.

### Actividad 2 — Esquema Criptográfico Híbrido RSA-OAEP + Scrypt + AES-GCM (`actividad_2/`)
- [`actividad_2/analizar_pcap.py`](./actividad_2/analizar_pcap.py): Inspector estructural y generador de volcados hexadecimales/ASCII de `transacciones_cifradas.pcap`.
- [`actividad_2/descifrar_transacciones.py`](./actividad_2/descifrar_transacciones.py): Script de recuperación del PIN (`4827`) con RSA-OAEP (SHA-256), derivación de clave AES-256 mediante `Scrypt(n=2**14, r=8, p=1)` y descifrado autenticado con `AESGCM`.
- [`actividad_2/hexdump_paquetes.txt`](./actividad_2/hexdump_paquetes.txt): Volcado hexadecimal y desglose de bytes de la trama inicial (`RSA_PIN|`) y las 40 tramas `AESGCM|`.
- [`actividad_2/salida_transacciones_completa.txt`](./actividad_2/salida_transacciones_completa.txt): Salida de las 40 transacciones financieras descifradas y autenticadas.

### Galería de Evidencias Visuales (`img/`)
- [`img/01_dockerfile_build.png`](./img/01_dockerfile_build.png): Construcción de imagen Docker `ssh-lab4` y verificación del contenedor `servidor-ssh` activo.
- [`img/02_sshd_config.png`](./img/02_sshd_config.png): Archivo `sshd_config` y verificación de algoritmos en memoria con `sshd -T`.
- [`img/03_ssh_conexion_cliente.png`](./img/03_ssh_conexion_cliente.png): Conexión cliente `ssh -vv` negociando los 4 algoritmos exigidos y ejecución remota.
- [`img/04_wireshark_ssh.png`](./img/04_wireshark_ssh.png): Inspección en Wireshark del tráfico SSH (banners, `SSH_MSG_KEXINIT` y paquetes cifrados).
- [`img/05_paquete_rsa_pin.png`](./img/05_paquete_rsa_pin.png): Identificación y hexdump de la trama #1 (`RSA_PIN|`: encabezado, salt de 16 B y criptograma RSA de 256 B).
- [`img/06_paquetes_aesgcm.png`](./img/06_paquetes_aesgcm.png): Filtrado y hexdump de las tramas `AESGCM|` (nonce de 12 B, texto cifrado y tag GCM de 16 B).
- [`img/07_codigo_pin_scrypt.png`](./img/07_codigo_pin_scrypt.png): Ejecución de extracción de salt, recuperación del PIN (`4827`) y derivación Scrypt.
- [`img/08_codigo_aesgcm.png`](./img/08_codigo_aesgcm.png): Validación de autenticidad e integridad de tags AES-GCM (40/40 íntegros).
- [`img/09_resultado_transacciones.png`](./img/09_resultado_transacciones.png): Ejecución del script con las transacciones recuperadas en formato oficial.
- [`img/codigo_script_parte1.jpg`](./img/codigo_script_parte1.jpg): Código fuente del script (Parte 1: Importaciones y argumentos).
- [`img/codigo_script_parte2.jpg`](./img/codigo_script_parte2.jpg): Código fuente del script (Parte 2: Parsing, RSA-OAEP y Scrypt).
- [`img/codigo_script_parte3.jpg`](./img/codigo_script_parte3.jpg): Código fuente del script (Parte 3: AES-GCM y exportación).

---

## Parámetros Criptográficos Recuperados (Actividad 2)

| Parámetro | Valor Obtenido |
|:---|:---|
| **Criptosistema Asimétrico** | RSA-2048 con relleno OAEP (`MGF1(SHA-256)`, `SHA-256`) |
| **Salt extraída (16 bytes, hex)** | `1a065da01a70284041b93dd58e988907` |
| **PIN recuperado** | **`4827`** |
| **KDF y Parámetros** | `Scrypt(salt, length=32, n=2**14 [16384], r=8, p=1)` |
| **Clave Simétrica AES-256 (32 bytes, hex)** | `f64d739ad8bd559fcd4bde7b9aecb83ff28d200331da635d7409b7133b16eab7` |
| **Esquema AEAD** | `AES-256-GCM` (`Nonce` = 12 bytes por trama, `Tag` = 16 bytes / 128 bits) |
| **Transacciones descifradas y autenticadas** | **40 / 40** (100% integridad verificada) |

---

## Tabla Completa de las 40 Transacciones Descifradas

| # | ID Transacción | Remitente (DE) | Destinatario (A) | Monto (CLP) |
|---:|:---|:---|:---|---:|
| 1 | `TRX-426477` | Diego Ramirez | Constanza Vidal | $763.923 |
| 2 | `TRX-346837` | Catalina Vargas | Valentina Rojas | $58.911 |
| 3 | `TRX-412154` | Sebastian Munoz | Constanza Vidal | $485.213 |
| 4 | `TRX-071484` | Felipe Morales | Tomas Sepulveda | $314.718 |
| 5 | `TRX-805221` | Isidora Silva | Javiera Fuentes | $104.470 |
| 6 | `TRX-971697` | Valentina Rojas | Camila Torres | $785.714 |
| 7 | `TRX-139273` | Catalina Vargas | Nicolas Herrera | $913.757 |
| 8 | `TRX-652114` | Camila Torres | Fernanda Araya | $855.548 |
| 9 | `TRX-432361` | Vicente Soto | Matias Gonzalez | $818.686 |
| 10 | `TRX-818929` | Antonia Castro | Tomas Sepulveda | $885.868 |
| 11 | `TRX-871181` | Catalina Vargas | Camila Torres | $514.444 |
| 12 | `TRX-157566` | Tomas Sepulveda | Javiera Fuentes | $436.301 |
| 13 | `TRX-186243` | Vicente Soto | Daniela Reyes | $698.110 |
| 14 | `TRX-121024` | Isidora Silva | Sebastian Munoz | $623.481 |
| 15 | `TRX-339097` | Matias Gonzalez | Constanza Vidal | $77.226 |
| 16 | `TRX-663549` | Isidora Silva | Antonia Castro | $576.901 |
| 17 | `TRX-367001` | Fernanda Araya | Tomas Sepulveda | $282.567 |
| 18 | `TRX-188807` | Camila Torres | Antonia Castro | $195.173 |
| 19 | `TRX-096936` | Felipe Morales | Antonia Castro | $359.917 |
| 20 | `TRX-695623` | Catalina Vargas | Nicolas Herrera | $619.299 |
| 21 | `TRX-407749` | Camila Torres | Sebastian Munoz | $182.369 |
| 22 | `TRX-069658` | Valentina Rojas | Javiera Fuentes | $556.520 |
| 23 | `TRX-232469` | Felipe Morales | Tomas Sepulveda | $23.769 |
| 24 | `TRX-940466` | Vicente Soto | Fernanda Araya | $292.293 |
| 25 | `TRX-755002` | Matias Gonzalez | Daniela Reyes | $946.989 |
| 26 | `TRX-962321` | Felipe Morales | Daniela Reyes | $589.780 |
| 27 | `TRX-324981` | Diego Ramirez | Daniela Reyes | $971.045 |
| 28 | `TRX-337011` | Antonia Castro | Felipe Morales | $777.198 |
| 29 | `TRX-995006` | Vicente Soto | Sebastian Munoz | $587.590 |
| 30 | `TRX-630572` | Camila Torres | Sebastian Munoz | $332.702 |
| 31 | `TRX-517969` | Catalina Vargas | Daniela Reyes | $484.770 |
| 32 | `TRX-447236` | Matias Gonzalez | Constanza Vidal | $331.352 |
| 33 | `TRX-852645` | Constanza Vidal | Felipe Morales | $343.065 |
| 34 | `TRX-188241` | Camila Torres | Constanza Vidal | $781.107 |
| 35 | `TRX-713923` | Diego Ramirez | Catalina Vargas | $21.358 |
| 36 | `TRX-362125` | Camila Torres | Sebastian Munoz | $154.118 |
| 37 | `TRX-961549` | Felipe Morales | Sebastian Munoz | $614.169 |
| 38 | `TRX-965060` | Tomas Sepulveda | Antonia Castro | $778.912 |
| 39 | `TRX-437498` | Valentina Rojas | Matias Gonzalez | $440.902 |
| 40 | `TRX-367112` | Matias Gonzalez | Isidora Silva | $91.711 |

**Monto total acumulado en las 40 transacciones:** `$19.671.946` CLP.

---

## Reproducción de Resultados

```bash
# Actividad 1: Construir y levantar servidor SSH en Docker
docker build -t ssh-lab4 actividad_1/
docker run -d -p 2222:22 --name servidor-ssh ssh-lab4
docker exec servidor-ssh sshd -T | grep -E "kexalgorithms|ciphers|macs|hostkeyalgorithms"

# Actividad 2: Analizar captura PCAP y descifrar las 40 transacciones
python3 actividad_2/analizar_pcap.py
python3 actividad_2/descifrar_transacciones.py
```
