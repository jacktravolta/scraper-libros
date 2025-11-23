import os
import requests
from bs4 import BeautifulSoup
from models.libro_modelo import crear_libro
from db.base_datos import guardar_libro, actualizar_libro
from utils.helpers import obtener_rating
from utils.tiempos import esperar
from utils.logger import log

# Leer URL base desde variable de entorno (.env)
BASE = os.getenv("URL_DESTINO", "https://books.toscrape.com/")
N_PAGINA = int(os.getenv("N_PAGINA", 4)) + 1
LIBROS_X_PAGINA = int(os.getenv("LIBROS_X_PAGINA", 5))

def scraper_bs4():
    """
    Scraper usando requests + BeautifulSoup.
    Extrae información del numero de paginas definidas en .env, guarda libros
    y luego procesa detalles de los primeros 5.
    """

    # Crear sesión HTTP para mejor rendimiento
    session = requests.Session()
    enlaces_detalle = []

    print("➡️ Iniciando scraping con BeautifulSoup...")
    log("INFO", "Iniciando scraping con BeautifulSoup")

    # --- Procesar páginas principales ---
    for pagina in range(1, N_PAGINA):

        url = BASE + f"catalogue/page-{pagina}.html"
        print(f"\n📄 Procesando página {pagina}: {url}")
        log("INFO", f"Procesando página: {url}")

        try:
            # Realizar petición HTTP
            respuesta = session.get(url, timeout=10)
            log("DEBUG", f"HTTP {respuesta.status_code} en página {pagina}")

            if respuesta.status_code != 200:
                print(f"❌ Error HTTP {respuesta.status_code} en página {pagina}")
                log("ERROR", f"HTTP {respuesta.status_code} en página {pagina}")
                continue

            # Parsear HTML
            soup = BeautifulSoup(respuesta.text, "html.parser")

            # Buscar componentes de libros
            articulos = soup.select("article.product_pod")
            print(f"   ✔ {len(articulos)} libros encontrados")
            log("DEBUG", f"{len(articulos)} libros encontrados en página {pagina}")

            for articulo in articulos[:LIBROS_X_PAGINA]:

                # Extraer datos del libro
                titulo = articulo.h3.a["title"]
                precio = articulo.select_one(".price_color").text.replace("£", "")
                disponibilidad = articulo.select_one(".availability").text.strip()
                rating = obtener_rating(articulo.p["class"][1])
                imagen_url = BASE + articulo.img["src"].replace("../", "")
                enlace = BASE + "catalogue/" + articulo.h3.a["href"]

                print(f"   ➕ Libro: {titulo}")
                log("INFO", f"Libro encontrado: {titulo}")
                log("DEBUG", f"Precio={precio}, Rating={rating}, URL={enlace}")

                # Crear objeto libro
                libro = crear_libro(titulo, precio, disponibilidad, rating, imagen_url)

                # Guardarlo en BD
                guardar_libro(libro)
                
                enlaces_detalle.append(enlace)

                esperar()

        except Exception as e:
            print(f"❌ Error en página {pagina}: {e}")
            log("ERROR", f"Error procesando página {pagina}: {e}")

    # --- Procesar detalles ---
    print(f"\n🔍 Procesando detalles de los primeros {LIBROS_X_PAGINA} libros...")
    log("INFO", "Iniciando scraping de detalles de libros")

    for enlace in enlaces_detalle[:LIBROS_X_PAGINA]:

        print(f"\n➡️ Procesando detalle: {enlace}")
        log("INFO", f"Procesando detalle: {enlace}")

        try:
            respuesta = session.get(enlace, timeout=10)

            if respuesta.status_code != 200:
                print(f"❌ No se pudo cargar detalle ({respuesta.status_code})")
                log("ERROR", f"No se pudo cargar detalle: {respuesta.status_code}")
                continue

            soup = BeautifulSoup(respuesta.text, "html.parser")

            # Descripción (si existe)
            descripcion_tag = soup.select_one("#product_description")
            descripcion = descripcion_tag.find_next("p").text if descripcion_tag else ""
            log("DEBUG", f"Descripción de {len(descripcion)} caracteres extraída")

            # Tabla de datos
            upc = soup.select("table tr td")[0].text
            categoria = soup.select("ul.breadcrumb li a")[-1].text
            titulo = soup.h1.text

            print(f"   ✏️ Actualizando libro: {titulo}")
            log("INFO", f"Actualizando libro: {titulo}")
            log("DEBUG", f"UPC={upc}, Categoría={categoria}")
            # Actualizar en la base
            actualizar_libro(titulo, descripcion, upc, categoria)

            print("   ✔ Datos de detalle actualizados")
            log("INFO", f"Detalle actualizado para {titulo}")

            esperar()

        except Exception as e:
            print(f"❌ Error en detalle {enlace}: {e}")
            log("ERROR", f"Error procesando detalle {enlace}: {e}")

    print("\n🏁 Scraping BeautifulSoup finalizado.")
    log("INFO", "Scraping BeautifulSoup finalizado")
