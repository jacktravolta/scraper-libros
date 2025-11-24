import os
import time
import random
from dotenv import load_dotenv
from utils.logger import log

# Carga las variables desde el archivo .env
load_dotenv()

# Obtiene el valor base de espera desde las variables de entorno.
# Si no existe, usa un valor por defecto de 2 segundos.
DELAY = int(os.getenv("DELAY_SEGUNDOS", "2"))

def esperar():
    """
    Pausa la ejecución del programa por un tiempo compuesto por:
    - un delay fijo obtenido desde el entorno
    - un pequeño valor aleatorio para evitar patrones predecibles

    También registra el tiempo real de espera.
    """
    
    # Calcula el tiempo final combinando delay y un margen aleatorio entre 0.2 y 0.8 s
    tiempo = DELAY + random.uniform(0.2, 0.8)

    # Registra el tiempo de pausa con dos decimales
    log("INFO", f"Pausa de {tiempo:.2f} segundos")

    # Detiene la ejecución durante el tiempo calculado
    time.sleep(tiempo)

