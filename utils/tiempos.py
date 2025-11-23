import os
import time
import random
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()

DELAY = int(os.getenv("DELAY_SEGUNDOS", "2"))

def esperar():
    tiempo = DELAY + random.uniform(0.2, 0.8)
    log("INFO", f"Pausa de {tiempo:.2f} segundos")
    time.sleep(tiempo)
