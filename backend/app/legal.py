"""Reglas del producto para personas de 17 años.

Estas reglas se aplican como una capa de orientación de producto. La web no reemplaza
la evaluación de un caso concreto ni la asesoría laboral.
"""

REGLAS_17 = {
    "edad": 17,
    "jornada_max_horas": 6,
    "trabajo_nocturno": False,
    "misma_paga_que_adulto": True,
    "denuncia": "SUNAFIL",
    "fuentes": ["Ley 27337", "Ley 30288"],
}


def oferta_apta_para_17(jornada_horas: float | None, trabajo_nocturno: bool = False) -> bool:
    if jornada_horas is None:
        return False
    return jornada_horas <= REGLAS_17["jornada_max_horas"] and not trabajo_nocturno


def texto_alerta_juvenil(apto_joven: bool) -> str:
    """Texto fijo para el punto 6 (alertas), sin inventar información legal nueva."""
    if apto_joven:
        return "Este puesto cumple los criterios juveniles de esta web."
    return "Ojo: este puesto no cumple los criterios que usamos para recomendar trabajos a jóvenes."
