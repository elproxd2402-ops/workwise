# WorkWise

Web mobile-first que ayuda a jóvenes de 17 a 20 años en Perú a comparar empresas, revisar reseñas, ver registros de sanciones SUNAFIL y detectar ofertas que pueden ser más fáciles de postular.

## Stack

- Frontend: Next.js 15 + React 19 + TypeScript
- Backend: FastAPI + SQLAlchemy
- BD: PostgreSQL 16
- IA: OpenAI API con `gpt-4o-mini`
- Deploy sugerido: Vercel (frontend) + Render (backend y PostgreSQL)

## Estructura

```text
workwise/
├── frontend/
│   ├── app/
│   │   ├── empresas/[id]/page.tsx
│   │   ├── derechos/page.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   ├── lib/api.ts
│   ├── Dockerfile
│   ├── .env.example
│   ├── package.json
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── ai_summary.py
│   │   ├── db.py
│   │   ├── legal.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── scoring.py
│   ├── scripts/
│   │   ├── batch_resumenes.py
│   │   └── import_data.py
│   ├── sql/
│   │   ├── 001_schema.sql
│   │   └── 002_demo_seed.sql
│   ├── Dockerfile
│   ├── .env.example
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 1. Ejecutar con Docker

Requisitos: Docker Desktop y Docker Compose.

```bash
git clone <tu-repositorio>
cd workwise

# opcional: crea un .env y agrega OPENAI_API_KEY si quieres regenerar resúmenes
cp backend/.env.example backend/.env

# levanta BD, API y frontend
docker compose up --build
```

Abre:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Documentación interactiva FastAPI: http://localhost:8000/docs

El compose carga datos ficticios de demostración para probar la interfaz. Esos datos no representan sanciones ni opiniones reales.

## 2. Ejecutar sin Docker

### PostgreSQL

Crea una base llamada `workwise` y ejecuta:

```bash
psql -U postgres -d workwise -f backend/sql/001_schema.sql
psql -U postgres -d workwise -f backend/sql/002_demo_seed.sql
# Si tu base ya existía antes de esta versión, ejecuta también:
psql -U postgres -d workwise -f backend/sql/003_es_demo.sql
```

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 3. Variables de entorno

Backend:

```env
OPENAI_API_KEY=
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workwise
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=workwise
FRONTEND_ORIGIN=http://localhost:3000
ADMIN_TOKEN=cambia-esto-en-produccion
```

Frontend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 4. Fórmula del puntaje

El backend calcula:

```text
Reputación       = promedio rating × 8       (0–40)
Cumplimiento     = max(0, 30 - 10 × sanciones)
Elegibilidad     = 20 si apto_joven, si no 0
Fácil de aplicar = 10 si NO exige título, si no 0
Total            = suma de los 4 componentes (0–100)
```

Semáforo:

```text
70–100 = verde
40–69  = amarillo
0–39   = rojo
```

## 5. Resúmenes con IA

El batch busca empresas sin `resumen_ia`, toma hasta 80 reseñas y llama a `gpt-4o-mini` usando el prompt especificado.

Desde `backend/`:

```bash
python -m scripts.batch_resumenes
```

También se puede regenerar desde la API. El endpoint está protegido con `X-Admin-Token` para evitar que visitantes anónimos gasten créditos de la API de IA:

```bash
curl -X POST http://localhost:8000/empresas/1/regenerar_resumen -H "X-Admin-Token: cambia-esto-en-produccion"
```

## 6. Importar datos de fuentes reales

Por seguridad y cumplimiento de términos de uso, este proyecto no trae un scraper directo de Glassdoor/Indeed. El importador está pensado para datos que obtengas mediante una API autorizada, exportación permitida o procesamiento propio con derecho de uso.

Ejemplo:

```bash
python -m scripts.import_data datos.json
```

Cada importación trata el JSON de una empresa como un **snapshot**: reemplaza sus reseñas, sanciones y ofertas existentes para evitar duplicados. Para una integración real conviene adaptar esto a un identificador estable de la fuente.

Formato:

```json
[
  {
    "empresa": {
      "nombre": "Empresa real",
      "sector": "Retail",
      "ciudad": "Lima",
      "exige_titulo": false,
      "apto_joven": true,
      "latitud": -12.0464,
      "longitud": -77.0428,
      "web_aplicacion": "https://empresa.pe/trabajos"
    },
    "resenas": [
      {
        "texto": "Buen ambiente...",
        "rating": 4,
        "fecha": "2026-07-10",
        "fuente": "Fuente autorizada",
        "url_fuente": "https://..."
      }
    ],
    "sanciones": [
      {
        "tipo": "Tipo de sanción",
        "fecha": "2026-02-20",
        "fuente": "SUNAFIL",
        "url_fuente": "https://..."
      }
    ],
    "ofertas": [
      {
        "titulo_puesto": "Auxiliar",
        "descripcion": "...",
        "requiere_titulo": false,
        "jornada_horas": 6,
        "apto_joven": true,
        "alertas": "...",
        "url_aplicacion": "https://..."
      }
    ]
  }
]
```

## 7. Endpoint principales

### `GET /empresas`

Filtros disponibles:

```text
q
sin_titulo=true
jornada_corta=true
seguro=true
cerca_de=Lima
ciudad=Lima
lat=-12.0464&lon=-77.0428
limit=40
```

### `GET /empresas/{id}`

Devuelve la empresa, desglose del puntaje, reseñas, sanciones y ofertas.

### `POST /empresas/{id}/regenerar_resumen`

Regenera el resumen de IA y guarda `actualizado_ia`.

### `GET /health`

Health check para Railway/VPS.

### `POST /admin/recalcular-puntajes`

Recalcula puntajes de todas las empresas. En producción, protégelo detrás de autenticación o una red privada antes de exponerlo públicamente.

## 8. Deploy público

La configuración incluida permite publicar el proyecto separando frontend, API y base de datos:

```text
Internet
   │
   ├── Vercel → frontend/ (Next.js)
   │       │
   │       └── NEXT_PUBLIC_API_URL → API de Render
   │
   └── Render → backend/ (FastAPI)
           │
           └── PostgreSQL de Render

OpenAI API → solo desde el backend
```

### A. GitHub

1. Crea un repositorio nuevo en GitHub.
2. Sube **todo el contenido de esta carpeta**, incluyendo `frontend/`, `backend/`, `render.yaml` y `vercel.json`.
3. **No subas archivos `.env` reales ni claves API.** El `.gitignore` del proyecto está preparado para evitarlo.

### B. Backend + PostgreSQL en Render

1. En Render, crea un **Blueprint** desde tu repositorio y selecciona `render.yaml`.
2. Render creará el servicio `workwise-api` y la base `workwise-db`.
3. En las variables del servicio agrega:
   - `OPENAI_API_KEY`: tu clave de OpenAI.
   - `FRONTEND_ORIGIN`: la URL final de Vercel, por ejemplo `https://tu-app.vercel.app`.
4. El backend usa `/health` como comprobación de salud.
5. Al arrancar por primera vez, el backend crea las tablas y, si la base está vacía, carga los datos **DEMO**. No borra una base que ya tenga empresas.

### C. Frontend en Vercel

1. Importa el mismo repositorio en Vercel.
2. Configura **Root Directory** como `frontend`.
3. En Environment Variables agrega:
   - `NEXT_PUBLIC_API_URL=https://tu-api.onrender.com`
4. Haz Deploy.
5. Copia la URL pública de Vercel y colócala en `FRONTEND_ORIGIN` en Render.

### D. Orden recomendado

Haz primero Render y después Vercel. Así tendrás la URL de la API cuando configures `NEXT_PUBLIC_API_URL`. Tras desplegar Vercel, vuelve a Render para completar `FRONTEND_ORIGIN`.

### E. Antes de compartir la web

Comprueba estas tres URLs: `https://tu-api.onrender.com/health`, la página principal de Vercel y `/asistente-cv`. Si el asistente de CV falla, revisa que `OPENAI_API_KEY` esté configurada **solo en Render**.

> Nota: los servicios gratuitos de algunos proveedores pueden suspenderse o tener límites. Para un lanzamiento público con usuarios reales, revisa precios, límites y condiciones actuales del proveedor antes de publicar.

## 9. Datos y legalidad

La aplicación distingue entre datos de reseñas y datos de sanciones. Para fuentes externas se guardan `fuente` y `url_fuente` cuando estén disponibles.

La página “Tus derechos” es educativa y no sustituye una evaluación legal. Las reglas del producto para una persona de 17 años están concentradas en `backend/app/legal.py` para que puedan actualizarse cuando corresponda. En un proyecto real conviene validar la versión vigente de la Ley 27337, la Ley 30288 y las reglas/criterios oficiales de SUNAFIL antes de publicar contenido legal como definitivo.

## 10. Accesibilidad y UX

- Mobile-first.
- Texto grande y contraste alto.
- Botones grandes.
- Filtros de un toque.
- Sin registro obligatorio para ver información.
- Navegación por teclado básica.
- Geolocalización solo cuando el usuario pulsa “Cerca de mí”.
- No se muestra ni se almacena la ubicación precisa del usuario en la base de datos.
