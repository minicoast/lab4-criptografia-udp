# Laboratorio 4 — Criptografía y Seguridad en Redes (2026)

Repositorio oficial de evidencias, código fuente, capturas de tráfico (`.pcap`), configuración de contenedor Docker SSH, claves criptográficas y resultados completos del **Laboratorio 4**.

---

## 📂 Estructura del Repositorio y Enlaces Directos

### 🔹 Raíz — Informe, Captura Original y Claves RSA
- 📄 [`informe_lab4.pdf`](./informe_lab4.pdf) — Informe técnico final compilado en PDF.
- 📝 [`informe_lab4.tex`](./informe_lab4.tex) — Código fuente completo del informe en LaTeX.
- 🌐 [`transacciones_cifradas.pcap`](./transacciones_cifradas.pcap) — Captura de red original con 1 paquete `RSA_PIN|` y 40 paquetes `AESGCM|`.
- 🔑 [`clave_publica.pem`](./clave_publica.pem) — Clave pública RSA-2048 proporcionada.
- 🔐 [`clave_privada.pem`](./clave_privada.pem) — Clave privada RSA-2048 utilizada para el descifrado RSA-OAEP (SHA-256).
- 🖼️ [`generar_capturas.py`](./generar_capturas.py) — Generador reproducible de las 9 capturas de evidencia en alta resolución.

### 🔹 Actividad 1 — Servidor OpenSSH en Docker y Análisis de Tráfico (`actividad_1/`)
- 🐳 [`actividad_1/Dockerfile`](./actividad_1/Dockerfile) — Construcción de imagen `ssh-lab4` sobre Ubuntu 22.04 con OpenSSH Server, `ssh-keygen -A` y validación `sshd -t`.
- ⚙️ [`actividad_1/sshd_config`](./actividad_1/sshd_config) — Configuración explícita de algoritmos criptográficos:
  - `KexAlgorithms curve25519-sha256`
  - `Ciphers aes256-ctr`
  - `MACs hmac-sha2-256`
  - `HostKeyAlgorithms ssh-ed25519` y `PubkeyAcceptedAlgorithms ssh-ed25519`
- 📡 [`actividad_1/captura_ssh.pcap`](./actividad_1/captura_ssh.pcap) — Captura real de tráfico de la sesión SSH en puerto TCP `2222` (56 tramas).
- 📋 [`actividad_1/ssh_vv_completo.log`](./actividad_1/ssh_vv_completo.log) — Registro íntegro del cliente `ssh -vv` negociando los 4 algoritmos y ejecutando comandos en el contenedor.
- 📋 [`actividad_1/ssh_vv_extracto.txt`](./actividad_1/ssh_vv_extracto.txt) — Extracto de líneas críticas de negociación criptográfica (`kex`, `cipher`, `MAC`, `host key`).
- 🔍 [`actividad_1/analisis_wireshark_ssh.txt`](./actividad_1/analisis_wireshark_ssh.txt) — Desglose completo de tramas, árbol de protocolo y volcado hexadecimal generado con Wireshark/`tshark`.
- 🧱 [`actividad_1/docker_build_log.txt`](./actividad_1/docker_build_log.txt) — Bitácora completa de `docker build`, `docker run`, `docker ps` y `sshd -T`.

### 🔹 Actividad 2 — Esquema Criptográfico Híbrido RSA-OAEP + Scrypt + AES-GCM (`actividad_2/`)
- 🐍 [`actividad_2/analizar_pcap.py`](./actividad_2/analizar_pcap.py) — Inspector estructural y generador de volcados hexadecimales/ASCII de `transacciones_cifradas.pcap`.
- 🐍 [`actividad_2/descifrar_transacciones.py`](./actividad_2/descifrar_transacciones.py) — Script de recuperación del PIN (`4827`) con RSA-OAEP (SHA-256), derivación de clave AES-256 con `Scrypt(n=2**14, r=8, p=1)` y descifrado autenticado con `AESGCM`.
- 📄 [`actividad_2/hexdump_paquetes.txt`](./actividad_2/hexdump_paquetes.txt) — Volcado hexadecimal y desglose de bytes del paquete #1 (`RSA_PIN|`) y los 40 paquetes `AESGCM|`.
- ✅ [`actividad_2/salida_transacciones_completa.txt`](./actividad_2/salida_transacciones_completa.txt) — Salida íntegra de las 40 transacciones financieras descifradas y autenticadas.

### 🔹 Galería de Evidencias Visuales (`img/`)
1. [`img/01_dockerfile_build.png`](./img/01_dockerfile_build.png) — Construcción de imagen Docker `ssh-lab4` y contenedor `servidor-ssh` activo.
2. [`img/02_sshd_config.png`](./img/02_sshd_config.png) — Archivo `sshd_config` y verificación activa mediante `sshd -T`.
3. [`img/03_ssh_conexion_cliente.png`](./img/03_ssh_conexion_cliente.png) — Conexión cliente `ssh -vv` negociando los 4 algoritmos y ejecutando comandos remotos.
4. [`img/04_wireshark_ssh.png`](./img/04_wireshark_ssh.png) — Inspección Wireshark/`tshark` de `captura_ssh.pcap` (banners, `SSH_MSG_KEXINIT` y `Encrypted packet`).
5. [`img/05_paquete_rsa_pin.png`](./img/05_paquete_rsa_pin.png) — Estructura y hexdump del paquete #1 (`RSA_PIN|`: header + `salt` 16 B + criptograma RSA 256 B).
6. [`img/06_paquetes_aesgcm.png`](./img/06_paquetes_aesgcm.png) — Listado y hexdump de los 40 paquetes `AESGCM|` (`nonce` 12 B + ciphertext + tag GCM 16 B).
7. [`img/07_codigo_pin_scrypt.png`](./img/07_codigo_pin_scrypt.png) — Código de extracción de `salt`, descifrado RSA-OAEP (SHA-256) y derivación `Scrypt`.
8. [`img/08_codigo_aesgcm.png`](./img/08_codigo_aesgcm.png) — Código de extracción de `nonce` y verificación/descifrado autenticado `AESGCM`.
9. [`img/09_resultado_transacciones.png`](./img/09_resultado_transacciones.png) — Ejecución en consola con el formato oficial de las transacciones descifradas.

---

## 🔑 Parámetros Criptográficos Recuperados (Actividad 2)

| Parámetro | Valor Obtenido |
|:---|:---|
| **Esquema Asimétrico** | RSA-2048 con relleno OAEP (`MGF1(SHA-256)`, `SHA-256`) |
| **Salt extraída (16 bytes, hex)** | `1a065da01a70284041b93dd58e988907` |
| **PIN recuperado** | **`4827`** |
| **KDF y Parámetros** | `Scrypt(salt, length=32, n=2**14 [16384], r=8, p=1)` |
| **Clave Simétrica AES-256 (32 bytes, hex)** | `f64d739ad8bd559fcd4bde7b9aecb83ff28d200331da635d7409b7133b16eab7` |
| **Esquema AEAD** | `AES-256-GCM` (`Nonce` = 12 bytes por paquete, `Tag` = 16 bytes / 128 bits) |
| **Transacciones autenticadas y descifradas** | **40 / 40** (0 errores de integridad) |

---

## 📊 Tabla Completa de las 40 Transacciones Descifradas

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

## 🖥️ Log Completo de Salida (`salida_transacciones_completa.txt`)

```text
[+] PIN recuperado mediante RSA
[+] PIN: 4827
[+] Transacciones cifradas encontradas: 40

========== TRANSACCIONES ==========

[Transacción 1]
TRANSACCION COMPLETADA|ID=TRX-426477|DE=Diego Ramirez|A=Constanza Vidal|MONTO=763923

[Transacción 2]
TRANSACCION COMPLETADA|ID=TRX-346837|DE=Catalina Vargas|A=Valentina Rojas|MONTO=58911

[Transacción 3]
TRANSACCION COMPLETADA|ID=TRX-412154|DE=Sebastian Munoz|A=Constanza Vidal|MONTO=485213

[Transacción 4]
TRANSACCION COMPLETADA|ID=TRX-071484|DE=Felipe Morales|A=Tomas Sepulveda|MONTO=314718

[Transacción 5]
TRANSACCION COMPLETADA|ID=TRX-805221|DE=Isidora Silva|A=Javiera Fuentes|MONTO=104470

[Transacción 6]
TRANSACCION COMPLETADA|ID=TRX-971697|DE=Valentina Rojas|A=Camila Torres|MONTO=785714

[Transacción 7]
TRANSACCION COMPLETADA|ID=TRX-139273|DE=Catalina Vargas|A=Nicolas Herrera|MONTO=913757

[Transacción 8]
TRANSACCION COMPLETADA|ID=TRX-652114|DE=Camila Torres|A=Fernanda Araya|MONTO=855548

[Transacción 9]
TRANSACCION COMPLETADA|ID=TRX-432361|DE=Vicente Soto|A=Matias Gonzalez|MONTO=818686

[Transacción 10]
TRANSACCION COMPLETADA|ID=TRX-818929|DE=Antonia Castro|A=Tomas Sepulveda|MONTO=885868

[Transacción 11]
TRANSACCION COMPLETADA|ID=TRX-871181|DE=Catalina Vargas|A=Camila Torres|MONTO=514444

[Transacción 12]
TRANSACCION COMPLETADA|ID=TRX-157566|DE=Tomas Sepulveda|A=Javiera Fuentes|MONTO=436301

[Transacción 13]
TRANSACCION COMPLETADA|ID=TRX-186243|DE=Vicente Soto|A=Daniela Reyes|MONTO=698110

[Transacción 14]
TRANSACCION COMPLETADA|ID=TRX-121024|DE=Isidora Silva|A=Sebastian Munoz|MONTO=623481

[Transacción 15]
TRANSACCION COMPLETADA|ID=TRX-339097|DE=Matias Gonzalez|A=Constanza Vidal|MONTO=77226

[Transacción 16]
TRANSACCION COMPLETADA|ID=TRX-663549|DE=Isidora Silva|A=Antonia Castro|MONTO=576901

[Transacción 17]
TRANSACCION COMPLETADA|ID=TRX-367001|DE=Fernanda Araya|A=Tomas Sepulveda|MONTO=282567

[Transacción 18]
TRANSACCION COMPLETADA|ID=TRX-188807|DE=Camila Torres|A=Antonia Castro|MONTO=195173

[Transacción 19]
TRANSACCION COMPLETADA|ID=TRX-096936|DE=Felipe Morales|A=Antonia Castro|MONTO=359917

[Transacción 20]
TRANSACCION COMPLETADA|ID=TRX-695623|DE=Catalina Vargas|A=Nicolas Herrera|MONTO=619299

[Transacción 21]
TRANSACCION COMPLETADA|ID=TRX-407749|DE=Camila Torres|A=Sebastian Munoz|MONTO=182369

[Transacción 22]
TRANSACCION COMPLETADA|ID=TRX-069658|DE=Valentina Rojas|A=Javiera Fuentes|MONTO=556520

[Transacción 23]
TRANSACCION COMPLETADA|ID=TRX-232469|DE=Felipe Morales|A=Tomas Sepulveda|MONTO=23769

[Transacción 24]
TRANSACCION COMPLETADA|ID=TRX-940466|DE=Vicente Soto|A=Fernanda Araya|MONTO=292293

[Transacción 25]
TRANSACCION COMPLETADA|ID=TRX-755002|DE=Matias Gonzalez|A=Daniela Reyes|MONTO=946989

[Transacción 26]
TRANSACCION COMPLETADA|ID=TRX-962321|DE=Felipe Morales|A=Daniela Reyes|MONTO=589780

[Transacción 27]
TRANSACCION COMPLETADA|ID=TRX-324981|DE=Diego Ramirez|A=Daniela Reyes|MONTO=971045

[Transacción 28]
TRANSACCION COMPLETADA|ID=TRX-337011|DE=Antonia Castro|A=Felipe Morales|MONTO=777198

[Transacción 29]
TRANSACCION COMPLETADA|ID=TRX-995006|DE=Vicente Soto|A=Sebastian Munoz|MONTO=587590

[Transacción 30]
TRANSACCION COMPLETADA|ID=TRX-630572|DE=Camila Torres|A=Sebastian Munoz|MONTO=332702

[Transacción 31]
TRANSACCION COMPLETADA|ID=TRX-517969|DE=Catalina Vargas|A=Daniela Reyes|MONTO=484770

[Transacción 32]
TRANSACCION COMPLETADA|ID=TRX-447236|DE=Matias Gonzalez|A=Constanza Vidal|MONTO=331352

[Transacción 33]
TRANSACCION COMPLETADA|ID=TRX-852645|DE=Constanza Vidal|A=Felipe Morales|MONTO=343065

[Transacción 34]
TRANSACCION COMPLETADA|ID=TRX-188241|DE=Camila Torres|A=Constanza Vidal|MONTO=781107

[Transacción 35]
TRANSACCION COMPLETADA|ID=TRX-713923|DE=Diego Ramirez|A=Catalina Vargas|MONTO=21358

[Transacción 36]
TRANSACCION COMPLETADA|ID=TRX-362125|DE=Camila Torres|A=Sebastian Munoz|MONTO=154118

[Transacción 37]
TRANSACCION COMPLETADA|ID=TRX-961549|DE=Felipe Morales|A=Sebastian Munoz|MONTO=614169

[Transacción 38]
TRANSACCION COMPLETADA|ID=TRX-965060|DE=Tomas Sepulveda|A=Antonia Castro|MONTO=778912

[Transacción 39]
TRANSACCION COMPLETADA|ID=TRX-437498|DE=Valentina Rojas|A=Matias Gonzalez|MONTO=440902

[Transacción 40]
TRANSACCION COMPLETADA|ID=TRX-367112|DE=Matias Gonzalez|A=Isidora Silva|MONTO=91711
```

---

## 🚀 Reproducción Rápida

```bash
# Actividad 1: Construir y levantar servidor SSH en Docker
docker build -t ssh-lab4 actividad_1/
docker run -d -p 2222:22 --name servidor-ssh ssh-lab4
docker exec servidor-ssh sshd -T | grep -E "kexalgorithms|ciphers|macs|hostkeyalgorithms"

# Actividad 2: Analizar captura PCAP y descifrar las 40 transacciones
python3 actividad_2/analizar_pcap.py
python3 actividad_2/descifrar_transacciones.py
```
