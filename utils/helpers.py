import os

# Nombre del archivo .env que contendrá las configuraciones del proyecto
ENV_FILE = ".env"

# Contenido predeterminado para el archivo .env en caso de que no exista.
# Incluye delays, nivel de logs, URL base, páginas a procesar, rutas, etc.
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
LIBROS_NAVEGA_DETALLE=5
"""

def crear_env_si_no_existe():
    """
    Crea un archivo .env con valores predeterminados si no existe.
    
    Esto asegura que la aplicación tenga siempre configuraciones mínimas 
    necesarias para ejecutarse, evitando errores por falta de variables
    de entorno.
    """
    # Verifica si el archivo .env no existe en la carpeta actual
    if not os.path.exists(ENV_FILE):
        # Lo crea y escribe los valores por defecto
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(ENV_DEFAULTS)

        # Mensaje informativo para el usuario
        print(f"✔ Archivo {ENV_FILE} creado con valores predeterminados.")
    

def obtener_rating(texto):
    """
    Convierte una palabra con el rating ('One', 'Two', etc.) 
    a un número entero entre 1 y 5.

    Si el texto no coincide con ninguna clave, devuelve 0.
    """
    mapa = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    # Retorna el valor correspondiente o 0 si no existe
    return mapa.get(texto, 0)


