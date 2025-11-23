# Proyecto Scraper de Libros

Este proyecto realiza scraping del sitio **Books to Scrape** usando:
- BeautifulSoup
- Selenium
- SQLite
- Sistema de logs
- Arquitectura modular

## 🚀 Instalación

```bash
git clone https://github.com/jacktravolta/scraper-libros
cd scraper-libros
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Variables de entorno (.env)

```
DELAY_SEGUNDOS=2
LOG_NIVEL=INFO
URL_DESTINO=https://books.toscrape.com/
N_PAGINA=4
LOG_ARCHIVO=logs.log
RUTA_BD=data/libros.db
```

## ▶️ Ejecución

```bash
python3 main.py
```

El programa permitirá elegir método:
- Scraping con BeautifulSoup  
- Scraping con Selenium

## 📂 Estructura del Proyecto

```
/project
 ├── main.py
 ├── scrapers/
 ├── utils/
 ├── models/
 ├── db/
 ├── data/
 └── README.md
```

## 🗃️ Base de Datos

La tabla `libros` almacena:
- título  
- precio  
- disponibilidad  
- rating  
- url_imagen  
- descripción  
- upc  
- categoría  
- fecha_extracción  

## 🧩 Funciones importantes

### ✔️ existe_libro(titulo)
Evita duplicados consultando si un libro ya está en la base de datos.

### ✔️ guardar_libro(libro)
Guarda un libro solo si **no existe previamente**.

### ✔️ actualizar_libro(...)
Actualiza detalles del libro (descripción, UPC, categoría).

---

## 📝 Logs

Todos los mensajes se guardan en el archivo definido en `.env`, por defecto: logs

```
logs.log
```

## 📦 Requerimientos

```
beautifulsoup4
requests
python-dotenv
sqlite3
selenium
```

---

## ✨ Autor
Proyecto Scraper de libros, diseñado y desarrollado por Juan Espinoza Castro. Contacto: juan.espinoza.castro88@gmail.com

