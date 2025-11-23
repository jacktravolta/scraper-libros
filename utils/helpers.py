def obtener_rating(texto):
    mapa = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return mapa.get(texto, 0)
