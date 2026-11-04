FROM ubuntu:22.04

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar paquetes e instalar OpenSSH Server y utilidades de red
RUN apt-get update && \
    apt-get install -y openssh-server iproute2 net-tools && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de ejecución requerido por sshd
RUN mkdir -p /var/run/sshd

# Generar las claves del host SSH (incluyendo /etc/ssh/ssh_host_ed25519_key)
RUN ssh-keygen -A

# Crear usuario de prueba con contraseña conocida para la conexión SSH
RUN useradd -m -s /bin/bash usuario && \
    echo "usuario:password123" | chpasswd

# Copiar configuración personalizada con los algoritmos criptográficos exigidos
COPY sshd_config /etc/ssh/sshd_config
RUN chmod 600 /etc/ssh/sshd_config && /usr/sbin/sshd -t

# Exponer el puerto estándar SSH
EXPOSE 22

# Ejecutar el demonio sshd en primer plano
CMD ["/usr/sbin/sshd", "-D", "-e"]
