import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Archivo donde se guardarán los logs (desde .env)
ARCHIVO_LOG = os.getenv("LOG_ARCHIVO", "logs.log")

def iniciar_logger():
    """Crear archivo si no existe."""
    open(ARCHIVO_LOG, "a").close()

def log(nivel, mensaje):
    """
    Escribe un log en formato texto.
    Ejemplo:
    [2025-01-12 12:00:00] [INFO] Inicio del proceso
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha}] [{nivel}] {mensaje}\n"

    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linea)

