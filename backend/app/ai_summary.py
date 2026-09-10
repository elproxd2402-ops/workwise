import os
from datetime import datetime, timezone

from openai import OpenAI

from .models import Empresa

PROMPT = (
    "Eres un asistente que ayuda a jóvenes de 17 a 20 años en Perú a elegir su primer empleo. "
    "Resume las siguientes reseñas en 2-3 frases cortas. Lenguaje muy sencillo, sin jerga. "
    "Si hay quejas graves dilo directo. Si hay aspectos positivos menciónalos. "
    "NO inventes datos numéricos.\n\nRESEÑAS:\n"
)


def generate_summary(empresa: Empresa) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en el entorno.")

    reviews = [r.texto.strip() for r in empresa.resenas if r.texto.strip()]
    if not reviews:
        return "Todavía no hay suficientes reseñas para resumir esta empresa."

    payload = "\n\n".join(f"- {text}" for text in reviews[:80])
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=140,
        messages=[
            {
                "role": "system",
                "content": "Escribe en español peruano simple. No inventes hechos ni cifras.",
            },
            {"role": "user", "content": PROMPT + payload},
        ],
    )
    summary = (response.choices[0].message.content or "").strip()
    if not summary:
        raise RuntimeError("La IA no devolvió un resumen.")
    return summary[:1000]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
