import sqlite3, os
from utils.logger import log

RUTA_BD = os.getenv("RUTA_BD", "data/libros.db")

def conectar():
    log("INFO", f"Conectando a la base de datos en {RUTA_BD}...")
    return sqlite3.connect(RUTA_BD)

# -----------------------------
# VERIFICAR SI YA EXISTE EL LIBRO
# -----------------------------
def existe_libro(titulo):
    conn = None  

    try:
        conn = conectar()
        cur = conn.cursor()

        log("INFO", f"Verificando si el libro ya existe: {titulo}")
        print(f"🔍 Verificando existencia: {titulo}")

        cur.execute("SELECT id FROM libros WHERE titulo = ?", (titulo,))
        existe = cur.fetchone() is not None

        if existe:
            log("INFO", f"El libro YA existe en la BD: {titulo}")
        else:
            log("INFO", f"El libro NO existe en la BD: {titulo}")

        return existe

    except Exception as e:
        print(f"❌ Error verificando libro {titulo}: {e}")
        log("ERROR", f"Error al verificar existencia: {e}")
        return False

    finally:
        if conn is not None:
            conn.close()

# -----------------------------
# CREACIÓN DE TABLAS
# -----------------------------
def crear_tablas():
    conn = None
    try:
        log("INFO", "Creando tablas si no existen...")
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT UNIQUE,
                precio DECIMAL(10,2),
                disponibilidad TEXT,
                rating INTEGER,
                url_imagen TEXT,
                descripcion TEXT,
                upc TEXT,
                categoria TEXT,
                fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        log("INFO", "Tablas creadas correctamente.")
    except Exception as e:
        log("ERROR", f"Error al crear tablas: {e}")
    finally:
        if conn is not None:
            conn.close()

# -----------------------------
# GUARDAR LIBRO
# -----------------------------
def guardar_libro(libro):
    conn = None  

    try:
        titulo = libro["titulo"]
        libro["precio"] = libro["precio"].replace("Â", "€")

        log("INFO", f"Intentando guardar libro: {titulo}")

        # Evitar duplicados antes de conectar
        if existe_libro(titulo):
            log("INFO", f"Se omitió guardar porque ya existe: {titulo}")
            print(f"⏩ Se omite (duplicado): {titulo}")
            return  # seguir ejecutando sin error

        conn = conectar()
        cur = conn.cursor()

        log("INFO", f"Insertando libro en la BD: {titulo}")

        cur.execute("""
            INSERT INTO libros (
                titulo, precio, disponibilidad, rating, url_imagen
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            libro["titulo"], libro["precio"], libro["disponibilidad"],
            libro["rating"], libro["imagen_url"]
        ))

        conn.commit()
        log("INFO", f"Libro guardado correctamente: {titulo}")
        
        if existe_libro(titulo):
            print(f"💾 Guardado en DB: {titulo}")

    except Exception as e:
        log("ERROR", f"Error al guardar libro: {e}")
        print(f"❌ Error al guardar {titulo}: {e}")

    finally:
        if conn is not None:
            conn.close()

# -----------------------------
# ACTUALIZAR LIBRO
# -----------------------------
def actualizar_libro(titulo, descripcion, upc, categoria):
    conn = None
    try:
        log("INFO", f"Actualizando libro: {titulo}")

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            UPDATE libros
            SET descripcion = ?, upc = ?, categoria = ?
            WHERE titulo = ?
        """, (descripcion, upc, categoria, titulo))

        conn.commit()

        if cur.rowcount == 0:
            log("WARNING", f"No se encontró el libro para actualizar: {titulo}")
        else:
            log("INFO", f"Libro actualizado: {titulo}")

    except Exception as e:
        log("ERROR", f"Error al actualizar libro: {e}")
    finally:
        if conn is not None:
            conn.close()
