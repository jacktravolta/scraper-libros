import os
# Nombre del archivo .env
ENV_FILE = ".env"

# Contenido predeterminado
ENV_DEFAULTS = """# Tiempo de espera entre requests (en segundos)
DELAY_SEGUNDOS=2

# Nivel de logs: DEBUG / INFO / WARNING / ERROR
LOG_NIVEL=INFO

# Nombre del archivo de logs
LOG_ARCHIVO=logs.log

# URL a scrapear
URL_DESTINO=https://books.toscrape.com/

# Número de páginas a procesar
N_PAGINA=3

# Ruta de la base de datos
RUTA_BD=data/libros.db

# Define cuántos libros por página procesará
LIBROS_X_PAGINA=5
"""

def crear_env_si_no_existe():
    """Crea un archivo .env con valores predeterminados si no existe."""
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(ENV_DEFAULTS)
        print(f"✅ Archivo {ENV_FILE} creado con valores predeterminados.")
    else:
        print(f"ℹ️ Archivo {ENV_FILE} ya existe, no se realizó ningún cambio.")

def obtener_rating(texto):
    mapa = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return mapa.get(texto, 0)

