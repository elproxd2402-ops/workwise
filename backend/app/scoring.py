from math import radians, sin, cos, sqrt, atan2


def semaforo(score: float) -> str:
    if score >= 70:
        return "verde"
    if score >= 40:
        return "amarillo"
    return "rojo"


def calcular_puntaje(avg_rating: float | None, sanciones: int, apto_joven: bool, exige_titulo: bool) -> float:
    """Fórmula base del proyecto.

    En las tarjetas de empresa, apto_joven/exige_titulo representan la mejor oferta
    registrada para un/a joven. Esto evita inflar artificialmente la puntuación por
    campos genéricos de la empresa, aunque el usuario debe revisar el puesto concreto
    antes de aplicar."""
    reputacion = (avg_rating or 0) * 8
    cumplimiento = max(0, 30 - (10 * sanciones))
    elegibilidad = 20 if apto_joven else 0
    facil = 10 if not exige_titulo else 0
    total = min(100, reputacion + cumplimiento + elegibilidad + facil)
    return round(total, 1)


def desglose_puntaje(avg_rating: float | None, sanciones: int, apto_joven: bool, exige_titulo: bool) -> dict:
    """Igual que calcular_puntaje pero devolviendo cada componente por separado,
    para poder mostrar la sección '¿Por qué tiene este puntaje?' sin repetir la
    fórmula en el frontend."""
    reputacion = round((avg_rating or 0) * 8, 1)
    cumplimiento = max(0, 30 - (10 * sanciones))
    elegibilidad = 20 if apto_joven else 0
    facil = 10 if not exige_titulo else 0
    total = min(100, round(reputacion + cumplimiento + elegibilidad + facil, 1))
    return {
        "reputacion": reputacion,
        "cumplimiento": cumplimiento,
        "elegibilidad_juvenil": elegibilidad,
        "facil_aplicar": facil,
        "total": total,
        "semaforo": semaforo(total),
    }


def mejor_oferta_referencia(ofertas: list) -> tuple[bool, bool]:
    """Elige qué oferta representa a la empresa para el cálculo del puntaje general
    de la tarjeta/listado: se prioriza la mejor oferta disponible (apta para joven
    y sin exigir título), porque es lo que más le interesa ver a un/a joven que
    busca trabajo. Si la empresa no tiene ninguna oferta registrada, se asume
    'no apta' y 'exige título' para no sobreestimar el puntaje sin datos.
    Devuelve (apto_joven, exige_titulo) de esa oferta de referencia."""
    if not ofertas:
        return False, True
    mejor = max(
        ofertas,
        key=lambda o: (1 if o.apto_joven else 0) + (1 if not o.requiere_titulo else 0),
    )
    return mejor.apto_joven, mejor.requiere_titulo


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(p1) * cos(p2) * sin(dlon / 2) ** 2
    return round(r * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)
