from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from models.libro_modelo import crear_libro
from db.base_datos import guardar_libro, actualizar_libro
from utils.logger import log
from utils.helpers import obtener_rating
from utils.tiempos import esperar
import os

# Leer URL desde .env, por si algún día quieres cambiar de sitio
BASE = os.getenv("URL_DESTINO", "https://books.toscrape.com/")
N_PAGINA = int(os.getenv("N_PAGINA", 4)) + 1

def scraper_selenium():
    """
    Scraper con Selenium: extrae libros del numeo de paginas definidos en .env
    y luego entra al detalle de los primeros 5 para obtener más info.
    """

    # Configurar Selenium en modo oculto
    opciones = Options()
    #opciones.add_argument("--headless")

    print("🟦 Iniciando Selenium (modo headless)...")
    log("INFO", "Iniciando Selenium...")

    # Crear driver
    driver = webdriver.Chrome(options=opciones)

    # Guardamos aquí los enlaces para procesar detalle
    enlaces = []

    # ---------------------------------------------
    # SCRAPING DE LISTA DE LIBROS
    # ---------------------------------------------
    for pagina in range(1, N_PAGINA):
        try:
            url = BASE + f"catalogue/page-{pagina}.html"

            print(f"\n📄 Cargando página {pagina}: {url}")
            log("INFO", f"Cargando página: {url}")

            # Abrir página
            driver.get(url)

            # Obtener lista de productos
            items = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

            print(f"   → {len(items)} libros encontrados")
            log("DEBUG", f"{len(items)} libros encontrados en página {pagina}")

            # Extraer información de cada libro
            for it in items:
                # Título
                titulo = (
                    it.find_element(By.TAG_NAME, "h3")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("title")
                )

                # Precio
                precio = it.find_element(By.CSS_SELECTOR, ".price_color").text.replace("£", "")

                # Disponibilidad
                disponibilidad = it.find_element(By.CSS_SELECTOR, ".availability").text.strip()

                # Rating
                clase = it.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class").split()[1]
                rating = obtener_rating(clase)

                # Imagen
                imagen_url = it.find_element(By.TAG_NAME, "img").get_attribute("src")

                # Link a detalle
                enlace = (
                    it.find_element(By.TAG_NAME, "h3")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                )

                print(f"   📘 Libro: {titulo}")
                log("INFO", f"Libro encontrado: {titulo}")

                # Crear objeto y guardar
                libro = crear_libro(titulo, precio, disponibilidad, rating, imagen_url)
                guardar_libro(libro)

               
                enlaces.append(enlace)

                esperar()

        except Exception as e:
            print(f"❌ Error procesando página {pagina}")
            log("ERROR", f"Error en Selenium página {pagina}: {e}")

    # ---------------------------------------------
    # SCRAPING DE DETALLE (5 primeros)
    # ---------------------------------------------
    print("\n🔍 Procesando detalles de los primeros 5 libros...")
    log("INFO", "Iniciando scraping de detalles...")

    for enlace in enlaces[:5]:
        try:
            print(f"\n➡️ Abriendo detalle: {enlace}")
            log("INFO", f"Abriendo detalle: {enlace}")

            driver.get(enlace)

            # Descripción
            desc_elementos = driver.find_elements(By.CSS_SELECTOR, "#product_description ~ p")
            descripcion = desc_elementos[0].text if desc_elementos else ""
            log("DEBUG", f"Descripción obtenida, largo={len(descripcion)}")

            # UPC
            filas = driver.find_elements(By.CSS_SELECTOR, "table.table tr")
            upc = filas[0].find_elements(By.TAG_NAME, "td")[0].text

            # Categoría
            categoria = driver.find_element(By.CSS_SELECTOR, "ul.breadcrumb li:nth-child(3) a").text

            # Título en detalle
            titulo = driver.find_element(By.TAG_NAME, "h1").text

            print(f"   📙 Actualizando libro: {titulo}")
            log("INFO", f"Actualizando detalles de: {titulo}")

            # Actualizar en la base
            actualizar_libro(titulo, descripcion, upc, categoria)

            print("      ✔ Detalles actualizados correctamente")
            log("INFO", f"Detalles actualizados: {titulo}")

            esperar()

        except Exception as e:
            print("❌ Error procesando detalle")
            log("ERROR", f"Error en detalle Selenium: {e}")

    # Cerrar Selenium
    print("\n🛑 Cerrando Selenium...")
    log("INFO", "Finalizando Selenium")

    driver.quit()
