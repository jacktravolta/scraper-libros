import sqlite3
import os
from utils.logger import log

# Ruta a la base de datos SQLite (tomada desde variable de entorno)
RUTA_BD = os.getenv("RUTA_BD", "data/libros.db")


# ------------------------------------------------
# CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------
def conectar():
    """Conecta a la base de datos SQLite y devuelve la conexión."""
    return sqlite3.connect(RUTA_BD)


# ------------------------------------------------
# VERIFICAR SI UN LIBRO YA EXISTE EN LA BD
# ------------------------------------------------
def existe_libro(titulo):
    conn = None
    try:
        conn = conectar()
        cur = conn.cursor()

        log("INFO", f"Verificando existencia del libro: {titulo}")
        print(f"\n🔍 Verificando existencia: {titulo}")

        # Consulta simple para comprobar si el título ya está registrado
        cur.execute("SELECT 1 FROM libros WHERE titulo = ? LIMIT 1", (titulo,))
        existe = cur.fetchone() is not None

        msg = "YA existe" if existe else "NO existe"
        log("INFO", f"El libro {msg} en la BD: {titulo}")

        return existe

    except Exception as e:
        # Manejo de errores durante la verificación
        log("ERROR", f"Error al verificar existencia: {e}")
        print(f"❌ Error verificando libro {titulo}: {e}")
        return False

    finally:
        # Se cierra siempre la conexión
        if conn:
            conn.close()


# ------------------------------------------------
# CREACIÓN DE TABLAS SI NO EXISTEN
# ------------------------------------------------
def crear_tablas():
    conn = None
    try:
        conn = conectar()
        cur = conn.cursor()

        # Comprueba si la tabla libros ya existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='libros';")
        if cur.fetchone():
            log("INFO", "La tabla 'libros' ya existe. No se creó nuevamente.")
            return

        # Creación de la tabla con todos los campos necesarios
        cur.execute("""
            CREATE TABLE libros (
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
        log("INFO", "Tabla 'libros' creada correctamente.")

    except Exception as e:
        # Registra cualquier error durante la creación
        log("ERROR", f"Error al crear tabla: {e}")

    finally:
        if conn:
            conn.close()


# ------------------------------------------------
# GUARDAR LIBRO EN LA BD (EVITA DUPLICADOS)
# ------------------------------------------------
def guardar_libro(libro):
    conn = None
    try:
        titulo = libro.get("titulo", "")

        # A veces BS4 trae caracteres raros; se normaliza el precio aquí
        libro["precio"] = libro.get("precio", "").replace("Â", "€")

        log("INFO", f"Intentando guardar libro: {titulo}")

        # Verifica primero si ya existe el libro
        if existe_libro(titulo):
            log("INFO", f"Omitido por duplicado: {titulo}")
            print(f"⏩ Se omite (duplicado): {titulo}")
            return

        conn = conectar()
        cur = conn.cursor()

        # Inserta los datos básicos
        cur.execute("""
            INSERT INTO libros (titulo, precio, disponibilidad, rating, url_imagen)
            VALUES (?, ?, ?, ?, ?)
        """, (
            titulo,
            libro.get("precio", "0.00"),
            libro.get("disponibilidad", ""),
            libro.get("rating", 0),
            libro.get("imagen_url", "")
        ))

        conn.commit()

        log("INFO", f"Libro guardado correctamente: {titulo}")
        print(f"💾 Guardado en DB: {titulo}")

    except Exception as e:
        # Manejo de errores en la inserción
        log("ERROR", f"Error al guardar libro: {e}")
        print(f"❌ Error al guardar {titulo}: {e}")

    finally:
        if conn:
            conn.close()


# ------------------------------------------------
# ACTUALIZAR DETALLES DEL LIBRO (DESCRIPCIÓN, UPC, CATEGORÍA)
# ------------------------------------------------
def actualizar_libro(titulo, descripcion="", upc="", categoria=""):
    conn = None
    try:
        log("INFO", f"Actualizando libro: {titulo}")

        conn = conectar()
        cur = conn.cursor()

        # Actualiza los campos de detalle
        cur.execute("""
            UPDATE libros
            SET descripcion = ?, upc = ?, categoria = ?
            WHERE titulo = ?
        """, (descripcion, upc, categoria, titulo))

        conn.commit()

        # rowcount indica si afectó alguna fila
        if cur.rowcount == 0:
            log("WARNING", f"No se encontró el libro para actualizar: {titulo}")
        else:
            log("INFO", f"Libro actualizado: {titulo}")

    except Exception as e:
        log("ERROR", f"Error al actualizar libro: {e}")

    finally:
        if conn:
            conn.close()
