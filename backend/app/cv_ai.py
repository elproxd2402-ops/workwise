import json
import os
from openai import OpenAI

CV_SYSTEM = """
Eres el asistente de CV de WorkWise, una app peruana que ayuda a jóvenes a prepararse para su primer empleo.
Tu trabajo es mejorar CVs sin inventar experiencias, estudios, cargos, empresas, idiomas, certificaciones, cifras ni habilidades.
Usa español claro y profesional. Si falta un dato, indícalo como pendiente.
No pidas ni incluyas DNI, dirección exacta, contraseñas, datos bancarios ni otros datos sensibles innecesarios.
Para una persona con poca o ninguna experiencia, puedes destacar proyectos escolares, voluntariado, cursos, habilidades y logros reales proporcionados por el usuario.
Devuelve SOLO JSON válido con estas claves:
{
  "cv": "CV completo en texto plano, listo para copiar",
  "correcciones": ["error o mejora 1", "..."],
  "fortalezas": ["fortaleza 1", "..."],
  "faltantes": ["dato útil que falta 1", "..."]
}
"""

def _call_ai(prompt: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en el entorno.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CV_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        max_tokens=1800,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": CV_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    raw = (response.choices[0].message.content or "").strip()
    if not raw:
        raise RuntimeError("La IA no devolvió una respuesta.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("La IA devolvió un formato inesperado.") from exc

    for key in ("cv", "correcciones", "fortalezas", "faltantes"):
        data.setdefault(key, [] if key != "cv" else "")
    return data

def generar_cv(datos: dict) -> dict:
    payload = json.dumps(datos, ensure_ascii=False, indent=2)
    return _call_ai(
        "Crea un CV de una página aproximadamente a partir de estos datos. "
        "No agregues información que no aparezca. Prioriza educación, habilidades, proyectos "
        "y experiencia real. Si hay errores ortográficos, corrígelos.\n\nDATOS:\n" + payload
    )

def revisar_cv(texto: str) -> dict:
    return _call_ai(
        "Revisa el siguiente CV. Corrige ortografía, redacción, orden y claridad. "
        "Mantén todos los hechos reales y no inventes información. Devuelve una versión mejorada "
        "y una lista breve de correcciones.\n\nCV:\n" + texto[:12000]
    )
