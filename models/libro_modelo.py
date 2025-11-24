def crear_libro(titulo, precio, disponibilidad, rating, imagen_url):
    # Crea y devuelve un diccionario que representa un libro
    return {
        "titulo": titulo,               # Título del libro
        "precio": precio,               # Precio del libro
        "disponibilidad": disponibilidad, # Disponibilidad (ej. "En stock")
        "rating": rating,               # Calificación (ej. 1–5 estrellas)
        "imagen_url": imagen_url,       # URL de la imagen de portada
        
        # Campos adicionales para completar más adelante
        "descripcion": None,            # Descripción del libro
        "upc": None,                    # UPC o código identificador
        "categoria": None               # Categoría a la que pertenece
    }
