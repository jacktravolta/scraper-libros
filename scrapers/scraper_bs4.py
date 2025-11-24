import os
import requests
from bs4 import BeautifulSoup
from models.libro_modelo import crear_libro
from db.base_datos import guardar_libro, actualizar_libro
from utils.helpers import obtener_rating
from utils.tiempos import esperar
from utils.logger import log
import random

# ---------------------------------------------------------
# CONFIGURACIÓN DEL SCRAPER A TRAVÉS DE VARIABLES DE ENTORNO
# ---------------------------------------------------------

# URL principal del sitio a scrapear
BASE = os.getenv("URL_DESTINO", "https://books.toscrape.com/")

# Cantidad de páginas de catálogo a recorrer
N_PAGINA = int(os.getenv("N_PAGINA", 4)) + 1

# Número de libros cuyos detalles serán consultados
LIBROS_NAVEGA_DETALLE = int(os.getenv("LIBROS_NAVEGA_DETALLE", 5))


def scraper_bs4():
    """
    Scraper utilizando Requests + BeautifulSoup.

    Fase 1:
        Recorre las páginas listadas en N_PAGINA,
        extrae los datos básicos de cada libro y los guarda en la base de datos.

    Fase 2:
        Selecciona aleatoriamente LIBROS_NAVEGA_DETALLE libros,
        visita sus páginas individuales y extrae información adicional
        como descripción, UPC y categoría.
    """

    # Crea una sesión para reutilizar conexión HTTP
    session = requests.Session()
    enlaces_detalle = []

    print("➡️ Iniciando scraping con BeautifulSoup...")
    log("INFO", "Iniciando scraping con BeautifulSoup")

    # ---------------------------------------------------------
    # 📌 1. SCRAPING DE LISTADO DE LIBROS
    # ---------------------------------------------------------
    for pagina in range(1, N_PAGINA):
        url = f"{BASE}catalogue/page-{pagina}.html"
        print(f"\n📄 Procesando página {pagina}: {url}")
        log("INFO", f"Procesando página: {url}")

        try:
            # Realiza request a la página del catálogo
            respuesta = session.get(url, timeout=10)
            log("DEBUG", f"HTTP {respuesta.status_code} en página {pagina}")

            # Si no responde 200, se omite
            if respuesta.status_code != 200:
                print(f"❌ Error HTTP {respuesta.status_code} en página {pagina}")
                log("ERROR", f"HTTP {respuesta.status_code} en página {pagina}")
                continue

            # Parsear HTML
            soup = BeautifulSoup(respuesta.text, "html.parser")

            # Encuentra cada contenedor de libro
            articulos = soup.select("article.product_pod")
            print(f"   ✔ {len(articulos)} libros encontrados")
            log("DEBUG", f"{len(articulos)} libros encontrados en página {pagina}")

            # Procesar cada libro detectado
            for articulo in articulos:

                # ----------- EXTRACCIÓN SEGURA DE DATOS ------------
                titulo_tag = getattr(articulo.h3.a, "get", lambda x: None)("title")
                precio_tag = articulo.select_one(".price_color")
                disponibilidad_tag = articulo.select_one(".availability")
                rating_tag = articulo.p
                imagen_tag = articulo.img
                href_tag = getattr(articulo.h3.a, "get", lambda x: None)("href")

                # Validación de título
                if not titulo_tag:
                    log("WARNING", "No se encontró título de un libro")
                    continue

                # Datos base
                titulo = titulo_tag
                precio = precio_tag.text.replace("£", "") if precio_tag else "0.00"
                disponibilidad = disponibilidad_tag.text.strip() if disponibilidad_tag else "Desconocida"

                # Rating obtenido desde clases CSS como "star-rating Three"
                rating = obtener_rating(rating_tag["class"][1]) if rating_tag and rating_tag.has_attr("class") else 0

                # URL completa de imagen
                imagen_url = BASE + imagen_tag["src"].replace("../", "") if imagen_tag else ""

                # Enlace absoluto al detalle
                enlace = BASE + "catalogue/" + href_tag if href_tag else ""

                log("INFO", f"Libro encontrado: {titulo}")
                log("DEBUG", f"Precio={precio}, Rating={rating}, URL={enlace}")

                # Crear y guardar libro en la base de datos
                libro = crear_libro(titulo, precio, disponibilidad, rating, imagen_url)
                guardar_libro(libro)

                # Guardamos enlace para posterior scraping de detalle
                enlaces_detalle.append(enlace)

        except Exception as e:
            print(f"❌ Error en página {pagina}: {e}")
            log("ERROR", f"Error procesando página {pagina}: {e}")

        # Espera para no saturar el sitio
        esperar()

    # ---------------------------------------------------------
    # 📌 2. SCRAPING DE DETALLE DE LIBROS
    # ---------------------------------------------------------

    total_detalle = min(LIBROS_NAVEGA_DETALLE, len(enlaces_detalle))

    print(f"\n🔍 Procesando detalle aleatorio de {total_detalle} libro{'s' if total_detalle > 1 else ''}...")
    log("INFO", f"Iniciando scraping de detalle de {total_detalle} libros")

    # Escoge enlaces aleatorios del total
    enlaces_detalle = random.sample(enlaces_detalle, total_detalle)

    for enlace in enlaces_detalle:
        print(f"\n➡️  Abriendo detalle: {enlace}")
        log("INFO", f"Abriendo detalle: {enlace}")

        try:
            respuesta = session.get(enlace, timeout=10)
            if respuesta.status_code != 200:
                print(f"❌ No se pudo cargar detalle ({respuesta.status_code})")
                log("ERROR", f"No se pudo cargar detalle: {respuesta.status_code}")
                continue

            soup = BeautifulSoup(respuesta.text, "html.parser")

            # Descripción del producto
            descripcion_tag = soup.select_one("#product_description")
            descripcion = descripcion_tag.find_next("p").text if descripcion_tag else ""
            if not descripcion_tag:
                log("WARNING", f"No se encontró la descripción en {enlace}")

            # UPC del libro (primer valor en tabla)
            table_cells = soup.select("table tr td")
            upc = table_cells[0].text if table_cells else ""
            if not table_cells:
                log("WARNING", f"No se encontró UPC en {enlace}")

            # Categoría dentro del breadcrumb
            breadcrumb = soup.select("ul.breadcrumb li a")
            categoria = breadcrumb[-1].text if breadcrumb and len(breadcrumb) >= 3 else ""
            if not breadcrumb or len(breadcrumb) < 3:
                log("WARNING", f"No se encontró categoría en {enlace}")

            # Título detallado
            titulo_h1 = soup.h1.text if soup.h1 else ""
            if not titulo_h1:
                log("WARNING", f"No se encontró título en detalle {enlace}")

            print(f"   ✏️ Actualizando libro: {titulo_h1}")
            log("INFO", f"Actualizando libro: {titulo_h1}")
            log("DEBUG", f"UPC={upc}, Categoría={categoria}")

            # Actualiza el registro del libro
            actualizar_libro(titulo_h1, descripcion, upc, categoria)

            print("   ✔ Datos de detalle actualizados")
            log("INFO", f"Detalle actualizado para {titulo_h1}")

            esperar()

        except Exception as e:
            print(f"❌ Error en detalle {enlace}: {e}")
            log("ERROR", f"Error procesando detalle {enlace}: {e}")

    print("\n🏁 Scraping BeautifulSoup finalizado.")
    log("INFO", "Scraping BeautifulSoup finalizado")
