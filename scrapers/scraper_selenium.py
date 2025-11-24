import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Funciones propias del proyecto
from models.libro_modelo import crear_libro
from db.base_datos import guardar_libro, actualizar_libro
from utils.logger import log
from utils.helpers import obtener_rating
from utils.tiempos import esperar

# -------------------------------------------------------------
# CONFIGURACIÓN DEL SCRAPER DESDE VARIABLES DE ENTORNO
# -------------------------------------------------------------

# URL base del sitio a scrapear
BASE = os.getenv("URL_DESTINO", "https://books.toscrape.com/")

# Número total de páginas a procesar (se suma 1 porque range() es exclusivo del final)
N_PAGINA = int(os.getenv("N_PAGINA", 4)) + 1

# Cantidad de libros cuyos detalles se abrirán de forma aleatoria
LIBROS_NAVEGA_DETALLE = int(os.getenv("LIBROS_NAVEGA_DETALLE", 5))


def scraper_selenium():
    """
    Scraper principal usando Selenium.

    Fase 1: Recorre las páginas del catálogo, extrae datos básicos y los guarda.
    Fase 2: Selecciona libros aleatoriamente y abre sus páginas de detalle,
            extrayendo información adicional (descripcion, UPC, categoria).
    """

    # Configura Chrome en modo headless (sin ventana visible)
    opciones = Options()
    opciones.add_argument("--headless")

    print("➡️ Iniciando Selenium (modo headless)...")
    log("INFO", "Iniciando Selenium...")

    # Inicia el driver de Chrome
    driver = webdriver.Chrome(options=opciones)
    enlaces_detalle = []  # Guarda enlaces individuales de cada libro

    # ---------------------------------------------------------
    # 📌 1. SCRAPING DE LA LISTA DE LIBROS
    # ---------------------------------------------------------
    for pagina in range(1, N_PAGINA):
        try:
            url = f"{BASE}catalogue/page-{pagina}.html"
            print(f"\n📄 Cargando página {pagina}: {url}")
            log("INFO", f"Cargando página: {url}")

            driver.get(url)

            # Obtiene los artículos que representan libros
            articulos = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

            print(f"   → {len(articulos)} libros encontrados")
            log("DEBUG", f"{len(articulos)} libros encontrados en página {pagina}")

            # Procesa cada libro encontrado
            for articulo in articulos:
                try:
                    # ---------- TÍTULO ----------
                    titulo_tag = articulo.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
                    titulo = titulo_tag.get_attribute("title") if titulo_tag else ""
                    if not titulo:
                        log("WARNING", "No se encontró título de un libro")
                        continue

                    # ---------- PRECIO ----------
                    precio_tag = articulo.find_elements(By.CSS_SELECTOR, ".price_color")
                    precio = precio_tag[0].text.replace("£", "") if precio_tag else "0.00"

                    # ---------- DISPONIBILIDAD ----------
                    disponibilidad_tag = articulo.find_elements(By.CSS_SELECTOR, ".availability")
                    disponibilidad = disponibilidad_tag[0].text.strip() if disponibilidad_tag else ""

                    # ---------- RATING ----------
                    rating_tag = articulo.find_elements(By.CSS_SELECTOR, "p.star-rating")
                    rating = obtener_rating(rating_tag[0].get_attribute("class").split()[1]) if rating_tag else 0

                    # ---------- IMAGEN ----------
                    imagen_tag = articulo.find_elements(By.TAG_NAME, "img")
                    imagen_url = imagen_tag[0].get_attribute("src") if imagen_tag else ""

                    # ---------- ENLACE AL DETALLE ----------
                    enlace = titulo_tag.get_attribute("href") if titulo_tag else ""

                    log("INFO", f"Libro encontrado: {titulo}")
                    log("DEBUG", f"Precio={precio}, Rating={rating}, URL={enlace}")

                    # Crea objeto libro y lo guarda en la BD
                    libro = crear_libro(titulo, precio, disponibilidad, rating, imagen_url)
                    guardar_libro(libro)

                    enlaces_detalle.append(enlace)

                except Exception as e:
                    print(f"❌ Error extrayendo libro en página {pagina}: {e}")
                    log("ERROR", f"Error extrayendo libro en página {pagina}: {e}")

        except Exception as e:
            print(f"❌ Error procesando página {pagina}: {e}")
            log("ERROR", f"Error en Selenium página {pagina}: {e}")

        # Espera aleatoria para evitar bloqueos del sitio
        esperar()

    # ---------------------------------------------------------
    # 📌 2. SCRAPING DE PÁGINA DE DETALLE DEL LIBRO
    # ---------------------------------------------------------

    total_detalle = min(LIBROS_NAVEGA_DETALLE, len(enlaces_detalle))
    print(f"\n🔍 Procesando detalle aleatorio de {total_detalle} libro{'s' if total_detalle > 1 else ''}...")
    log("INFO", f"Iniciando scraping de detalle de {total_detalle} libros")

    # Selecciona enlaces aleatorios entre todos los encontrados
    enlaces_detalle = random.sample(enlaces_detalle, total_detalle)

    for enlace in enlaces_detalle:
        try:
            print(f"\n➡️  Abriendo detalle: {enlace}")
            log("INFO", f"Abriendo detalle: {enlace}")

            driver.get(enlace)

            # ---------- DESCRIPCIÓN ----------
            descripcion_tag = driver.find_elements(By.CSS_SELECTOR, "#product_description ~ p")
            descripcion = descripcion_tag[0].text if descripcion_tag else ""

            # ---------- UPC ----------
            filas = driver.find_elements(By.CSS_SELECTOR, "table.table tr")
            if filas and filas[0].find_elements(By.TAG_NAME, "td"):
                upc = filas[0].find_elements(By.TAG_NAME, "td")[0].text
            else:
                upc = ""

            # ---------- CATEGORÍA ----------
            try:
                categoria_tag = driver.find_element(By.CSS_SELECTOR, "ul.breadcrumb li:nth-child(3) a")
                categoria = categoria_tag.text
            except:
                categoria = ""

            # ---------- TÍTULO EN LA PÁGINA DE DETALLE ----------
            try:
                titulo_h1_tag = driver.find_element(By.TAG_NAME, "h1")
                titulo_h1 = titulo_h1_tag.text
            except:
                titulo_h1 = ""

            print(f"   ✏️ Actualizando libro: {titulo_h1}")
            log("INFO", f"Actualizando detalles de: {titulo_h1}")
            log("DEBUG", f"UPC={upc}, Categoría={categoria}")

            # Actualiza el libro en la base de datos
            actualizar_libro(titulo_h1, descripcion, upc, categoria)

            print("      ✔ Detalles actualizados correctamente")
            log("INFO", f"Detalles actualizados: {titulo_h1}")

            esperar()

        except Exception as e:
            print(f"❌ Error procesando detalle: {e}")
            log("ERROR", f"Error en detalle Selenium: {e}")

    # Cierra el navegador al finalizar
    driver.quit()
    print("\n🏁 Scraping Selenium finalizado.")
    log("INFO", "Scraping Selenium finalizado")
