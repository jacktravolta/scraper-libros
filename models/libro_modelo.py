import os
from datetime import datetime
from dotenv import load_dotenv

# Carga variables de entorno desde el archivo .env
load_dotenv()

# Archivo donde se guardarán los logs, configurable desde .env
# Si la variable LOG_ARCHIVO no existe, usa "logs.log" por defecto
ARCHIVO_LOG = os.getenv("LOG_ARCHIVO", "logs.log")


def iniciar_logger():
    """
    Crea el archivo de logs si no existe.
    Utiliza modo 'a' (append) para no sobrescribir contenido previo.
    """
    open(ARCHIVO_LOG, "a").close()


def log(nivel, mensaje):
    """
    Escribe una línea de log en el archivo configurado.

    Formato del log:
    [YYYY-MM-DD HH:MM:SS] [NIVEL] Mensaje

    Ejemplo:
    [2025-01-12 12:00:00] [INFO] Inicio del proceso
    """

    # Obtiene la fecha y hora actual en formato legible
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construye el texto de la línea del log
    linea = f"[{fecha}] [{nivel}] {mensaje}\n"

    # Abre el archivo en modo append y escribe la línea
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linea)


