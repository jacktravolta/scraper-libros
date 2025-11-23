import os
from dotenv import load_dotenv
from utils.logger import iniciar_logger, log
from scrapers.scraper_bs4 import scraper_bs4
from scrapers.scraper_selenium import scraper_selenium
from db.base_datos import crear_tablas
from utils.helpers import crear_env_si_no_existe

# Cargar variables de entorno desde .env
load_dotenv()

def menu(): 
    """Muestra un menú simple para seleccionar el tipo de scraping."""
    
    print("\n==============================")
    print("     SCRAPER DE LIBROS")
    print("==============================")
    print("1. Scraping con BeautifulSoup")
    print("2. Scraping con Selenium")
    print("==============================\n")

    opcion = input("Seleccione una opción: ").strip()

    # Ejecuta según la opción seleccionada
    if opcion == "1":
        log("INFO", "Usuario seleccionó BeautifulSoup")
        scraper_bs4()
 
    elif opcion == "2":
        log("INFO", "Usuario seleccionó Selenium")
        scraper_selenium()
 
    else:
        log("ERROR", f"Opción inválida ingresada: {opcion}")
        print("❌ Opción no válida. Intente de nuevo.\n")

if __name__ == "__main__":
    print("Inicializando sistema...\n")

    # Crear .env con datos predeterminados si no existe
    print("✔ .env verificado / creado.")
    crear_env_si_no_existe()

    # Crear archivo de log si no existe
    iniciar_logger()
    print("✔ Logger iniciado.")

    # Crear tablas de la base si no existen
    crear_tablas()
    print("✔ Tablas verificadas / creadas.")

    # Llamar al menú principal
    menu()

    print("Programa finalizado.")
