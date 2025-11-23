def crear_libro(titulo, precio, disponibilidad, rating, imagen_url):
    return {
        "titulo": titulo,
        "precio": precio,
        "disponibilidad": disponibilidad,
        "rating": rating,
        "imagen_url": imagen_url,
        "descripcion": None,
        "upc": None,
        "categoria": None
    }
