# ADIPA — Backend (Quiz Extraction API)

> API que recibe un documento (PDF, Word o Excel), extrae las preguntas y alternativas, las clasifica por tipo y retorna un JSON estructurado.

> **Caso de uso objetivo:** herramienta pensada para el flujo editorial de ADIPA — convertir material evaluativo legado (exámenes en PDF/Word/Excel) en formato estructurado apto para integrarse al LMS de diplomados y cursos de especialización en psicología clínica.

---

## 🔗 Demo en producción

- **API base:** _pendiente de deploy_
- **Docs (Swagger UI):** _pendiente de deploy_ `/docs`

---

## ✨ Características

- 📄 Soporte para **PDF**, **DOCX** y **XLSX**
- 🧠 Clasificación automática en 4 tipos: `seleccion_multiple`, `verdadero_falso`, `desarrollo`, `emparejamiento`
- ✅ Extracción de **respuesta correcta** cuando está explícita en el documento
- 🛡️ Manejo de errores específicos con códigos HTTP semánticos (400 / 422 / 502)
- 🇪🇸 JSON de salida en español (cumple contrato del enunciado)
- 🧪 Tests unitarios por capa con fakes (sin tocar Groq real)

---

## 🛠️ Stack técnico

| Capa | Tecnología |
|---|---|
| Framework web | FastAPI 0.111+ |
| LLM | [Groq](https://console.groq.com) (API compatible OpenAI) |
| Modelo | `llama-3.1-8b-instant` (configurable) |
| Parseo PDF | `pdfplumber` |
| Parseo Word | `python-docx` |
| Parseo Excel | `openpyxl` |
| Configuración | `pydantic-settings` (archivo `.env`) |
| Testing | `pytest` |

---

## 🏗️ Arquitectura

**Clean Architecture / Hexagonal** con 4 capas por módulo:

```
domain/          → Entidades puras, sin dependencias externas
application/     → Lógica de negocio, expone puertos (interfaces)
infrastructure/  → Adaptadores concretos (LLM, parsers de archivos)
presentation/    → Capa HTTP (routers + DTOs)
```

**Principio clave:** la capa `application/` **no conoce** Groq ni pdfplumber. Depende de puertos (`TextExtractorPort`, `QuestionExtractorPort`). Los adaptadores en `infrastructure/` los implementan. Esto permite:

- **Testear** el service con fakes, sin tocar red ni APIs.
- **Cambiar de LLM** (Groq → Gemini/Ollama/OpenAI) sin modificar lógica de negocio.
- **Agregar formatos** (ej: Markdown, OCR) creando nuevos extractores sin tocar el core.

---

## 📁 Estructura del proyecto

```
adipa-challenge-backend/
├── src/
│   ├── config.py                       # Settings con pydantic-settings
│   ├── main.py                         # FastAPI app + CORS + routers
│   ├── health/                         # módulo health-check
│   └── quiz_extraction/                # módulo principal
│       ├── domain/
│       │   ├── question.py             # Question, QuestionAlternative, QuestionType
│       │   └── quiz_result.py          # QuizResult
│       ├── application/
│       │   ├── ports/                  # interfaces (ABC)
│       │   │   ├── text_extractor_port.py
│       │   │   └── question_extractor_port.py
│       │   └── services/
│       │       └── quiz_extraction_service.py
│       ├── infrastructure/
│       │   ├── text_extractors/        # PDF/DOCX/XLSX + dispatcher
│       │   └── llm/
│       │       ├── groq_question_extractor.py
│       │       └── prompts/
│       │           └── quiz_extraction.md   # prompt como contenido
│       └── presentation/
│           ├── dtos/
│           │   └── quiz_dtos.py        # DTOs con aliases ES
│           └── routers/
│               └── quiz_router.py      # POST /quiz/extract
├── tests/                              # mirror de src/ con pytest
├── examples/                           # archivos de prueba + JSON de respuesta
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Setup local

### Requisitos

- Python 3.10+
- Cuenta gratuita en [Groq](https://console.groq.com) para obtener una API key

### Pasos

```cmd
# 1. Clonar el repositorio
git clone <url-del-repo>
cd adipa-challenge-backend

# 2. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate.bat              # Windows (CMD)
# source .venv/bin/activate              # macOS/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env                   # Windows
# cp .env.example .env                    # macOS/Linux
# Editar .env y reemplazar la API key

# 5. Correr el servidor
uvicorn src.main:app --reload
```

La API queda en `http://localhost:8000`. Abre `http://localhost:8000/docs` para la documentación interactiva.

---

## ☁️ Deploy en Railway

El proyecto incluye un `railway.json` listo para desplegar en [Railway](https://railway.com).

### Pasos

1. **Crear cuenta** en [railway.com](https://railway.com) y conectar GitHub.
2. **New Project → Deploy from GitHub repo** → selecciona este repositorio.
3. **Configurar root directory** (clave en monorepo):
   - Project settings → **Root Directory** = `adipa-challenge-backend`
4. **Agregar variables de entorno** (Settings → Variables):
   ```
   GROQ_API_KEY=gsk_xxxxx
   GROQ_MODEL=llama-3.1-8b-instant
   GROQ_TEMPERATURE=0.2
   GROQ_MAX_TOKENS=4096
   ```
5. **Generar dominio público** (Settings → Networking → Generate Domain). Railway te da una URL tipo `adipa-challenge-backend-production.up.railway.app`.
6. **Actualizar README** con la URL real en "Demo en producción".

### Cómo funciona

- Railway usa [Nixpacks](https://nixpacks.com) para detectar Python y ejecutar `pip install -r requirements.txt`.
- `.python-version` fija Python 3.12.
- `railway.json` declara el comando de arranque (`uvicorn ... --port $PORT`) y el health check en `/health`.
- Railway inyecta `$PORT` automáticamente en cada deploy.

### Redeploy automático

Cada `git push` al branch configurado (típicamente `main`) dispara un deploy nuevo.

---

## 🔐 Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `GROQ_API_KEY` | API key de Groq (obtener en [console.groq.com](https://console.groq.com)) | **requerida** |
| `GROQ_MODEL` | Modelo a usar | `llama-3.1-8b-instant` |
| `GROQ_TEMPERATURE` | Creatividad del LLM (0.0 = determinista, 2.0 = muy creativo) | `0.2` |
| `GROQ_MAX_TOKENS` | Máximo de tokens en la respuesta | `4096` |

---

## 🧪 Tests

```cmd
pytest -v
```

Corre 6 tests en <1 segundo:
- **Service** (3): happy path, no-questions-found, propagación de errores
- **Dispatcher** (2): formato no soportado + case-insensitivity
- **DTO** (1): serialización con aliases en español

**No se requiere** API key de Groq ni archivos reales — los tests usan **fakes** de los puertos.

---

## 📡 Uso de la API

### `POST /quiz/extract`

Sube un archivo y obtén las preguntas estructuradas.

**Ejemplo con `curl`:**

```cmd
curl -X POST http://localhost:8000/quiz/extract ^
  -F "file=@examples/quiz_ejemplo.pdf"
```

**Respuesta exitosa (200):**

```json
{
  "total_preguntas": 2,
  "preguntas": [
    {
      "numero": 1,
      "enunciado": "¿Cuál es la capital de Chile?",
      "tipo": "seleccion_multiple",
      "alternativas": [
        { "letra": "A", "texto": "Lima" },
        { "letra": "B", "texto": "Santiago" },
        { "letra": "C", "texto": "Bogotá" }
      ],
      "respuesta_correcta": "B"
    },
    {
      "numero": 2,
      "enunciado": "El agua hierve a 100°C al nivel del mar.",
      "tipo": "verdadero_falso",
      "alternativas": [],
      "respuesta_correcta": "Verdadero"
    }
  ]
}
```

### Códigos de error

| Código | Cuándo |
|---|---|
| **400** Bad Request | Formato no soportado (ej: `.txt`) |
| **422** Unprocessable Entity | No se detectaron preguntas en el documento |
| **502** Bad Gateway | Fallo del LLM (timeout, JSON inválido, rate limit) |

---

## 📄 Archivos de ejemplo

En `examples/` encuentras:

| Archivo | Contenido |
|---|---|
| `quiz_ejemplo.pdf` | Examen completo (13 preguntas, 4 tipos) — Diplomado en Psicopatología Infantojuvenil |
| `quiz_ejemplo.docx` | Mismo examen en Word con tablas nativas para emparejamiento |
| `quiz_ejemplo.xlsx` | Mismo examen en formato tabular (12 preguntas — ver nota) |
| `quiz_ejemplo_resultado.json` | JSON de respuesta esperada (aplica a los 3 formatos) |

> **Nota sobre XLSX:** el formato tabular de Excel no acomoda bien preguntas de emparejamiento (que requieren dos columnas relacionadas). Por eso el ejemplo Excel omite la pregunta #13. Esto refleja un caso real: en flujos editoriales, el tipo de contenido determina el formato más apropiado.

---

## 🎯 Decisiones técnicas

### Groq como proveedor de LLM

Elegido sobre OpenAI/Gemini por:
- **Free tier generoso** para la prueba
- **Inferencia en LPUs** → respuestas muy rápidas (<1s típicamente)
- **JSON mode** nativo (`response_format={"type": "json_object"}`) garantiza salida parseable
- **API compatible con OpenAI** → swap trivial si se necesita

### Modelo `llama-3.1-8b-instant`

Para esta prueba prioricé **velocidad sobre máxima calidad**. Si el evaluador lo prefiere, basta cambiar `GROQ_MODEL=llama-3.3-70b-versatile` en `.env` — el código no cambia.

### Clean Architecture

El enunciado no lo exige, pero separar en capas:
1. Demuestra pensamiento arquitectónico
2. Facilita testeo con fakes
3. Permite extensibilidad (agregar OCR, más formatos, otros LLMs) sin tocar el core

### Dominio en inglés, JSON en español

El **dominio Python** usa identificadores en inglés (`number`, `content`, `alternatives`, etc.) — estándar de la industria y mejor legibilidad. El **contrato HTTP** usa español (`numero`, `enunciado`, etc.) por exigencia del enunciado. El mapeo se hace en la capa `presentation/` con `Field(alias="...")` de Pydantic.

### Prompt engineering con few-shot

El prompt vive en `infrastructure/llm/prompts/quiz_extraction.md` (no como string Python) para:
- Separar **contenido** de **código**
- Editar sin tocar Python (git diffs limpios)
- Facilitar experimentos A/B con versiones del prompt

Incluye **3 ejemplos few-shot** cubriendo casos clave (selección múltiple, V/F + desarrollo mezclados, emparejamiento). Mejora significativamente la calidad del modelo 8b.

### Excepciones tipadas → HTTP status semánticos

En vez de un `except Exception: return 500`, cada error del dominio tiene su excepción propia:

| Excepción | HTTP |
|---|---|
| `UnsupportedFileFormatError` | 400 |
| `NoQuestionsFoundError` | 422 |
| `QuestionExtractionError` | 502 |

El cliente recibe información accionable.

### Contexto del negocio

ADIPA opera cursos y diplomados en psicología y salud mental con más de 100,000 estudiantes. El caso de uso probable para esta herramienta es **digitalizar evaluaciones legadas** (exámenes en PDF/Word que viven en archivos de profesores) y convertirlas a estructura importable al LMS. Por eso prioricé:

- **Robustez ante variabilidad de formato** — PDFs con layout académico, Word con párrafos estructurados, Excel tabular.
- **Clasificación precisa del tipo** — crítica para que el LMS sepa cómo renderizar cada pregunta (radio buttons para selección múltiple, textarea para desarrollo, etc.).
- **Detección opcional de respuesta correcta** — algunos exámenes la incluyen en el documento (exámenes ya corregidos o con clave), otros no.
- **Prompt especializado en dominio clínico** — el LLM reconoce terminología DSM-5, trastornos psiquiátricos, enfoques terapéuticos, neurotransmisores, etc.

---

## ⚠️ Supuestos y limitaciones

- **PDFs escaneados (imágenes sin OCR):** `pdfplumber` solo extrae texto nativo. Un PDF que es foto de una página no devolverá texto → HTTP 422. Se podría agregar OCR con `pytesseract` si fuera necesario.
- **Tablas en Word:** `python-docx` aquí solo procesa párrafos. Preguntas dentro de tablas de Word no serán extraídas en esta versión.
- **Formato de emparejamiento:** el LLM recibe el texto tabular y clasifica el tipo. Como el enunciado no especifica cómo representar el emparejamiento (pares en JSON vs texto continuo), el adaptador actual deja `alternatives: []` y preserva el contenido completo en `content`. **Supuesto documentado:** por consistencia con V/F y desarrollo (que también tienen `alternatives: []`).
- **Tamaño máximo de archivo:** no hay límite explícito en esta versión. En producción se debería validar (ej: 10MB).
- **Idioma:** el LLM fue probado con documentos en español. Otros idiomas pueden funcionar pero no se garantiza.

---

## 👤 Autor

Johnny Bernal — [bernaljohnny3@gmail.com](mailto:bernaljohnny3@gmail.com)
