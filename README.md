# DocuWise

DocuWise es un sistema de **Retrieval-Augmented Generation (RAG)** diseñado para realizar consultas sobre documentación proporcionada por el usuario.

El sistema permite cargar documentos, procesarlos, dividirlos en fragmentos, generar embeddings, almacenarlos en una base de datos vectorial y posteriormente recuperar la información más relevante para responder preguntas utilizando un modelo de lenguaje.

El objetivo de esta primera versión es construir un pipeline RAG funcional, modular, evaluado y documentado.

---

## Características

* Carga de documentos mediante API REST.
* Soporte para documentos:

  * PDF
  * DOCX
  * Markdown (`.md`)
* Validación de formatos de archivo.
* Extracción y normalización del contenido.
* División del contenido mediante chunking recursivo.
* Generación de embeddings.
* Almacenamiento de vectores en Qdrant.
* Recuperación semántica mediante búsqueda vectorial.
* Filtrado mediante un umbral mínimo de relevancia.
* Orquestación del proceso RAG mediante LangGraph.
* Generación de respuestas mediante un modelo de lenguaje de OpenAI.
* Respuestas basadas exclusivamente en el contexto recuperado.
* Protección frente a instrucciones incluidas en las preguntas o documentos que intenten modificar el comportamiento del sistema.
* Inclusión de fuentes y páginas utilizadas para generar la respuesta.
* Respuesta controlada cuando no existe contexto suficientemente relevante.
* Evaluación mediante métricas de recuperación.
* Documentación técnica del proyecto.

---

## Arquitectura

El funcionamiento general de DocuWise puede dividirse en dos pipelines principales:

### Pipeline de ingesta

```text
Documento
    │
    ▼
Upload API
    │
    ▼
Parser
    │
    ▼
Extracción del contenido
    │
    ▼
Recursive Chunking
    │
    ▼
Embeddings
    │
    ▼
Qdrant
```

### Pipeline de consulta

```text
Pregunta del usuario
        │
        ▼
Generación del embedding
        │
        ▼
Búsqueda semántica en Qdrant
        │
        ▼
Resultados relevantes
        │
        ▼
Comprobación del contexto
        │
        ├── Contexto insuficiente
        │       │
        │       ▼
        │   Respuesta controlada
        │
        └── Contexto suficiente
                │
                ▼
          Construcción del prompt
                │
                ▼
              LLM
                │
                ▼
      Respuesta + fuentes
```

La arquitectura completa está explicada en:

* [`docs/architecture.md`](docs/architecture.md)
* [`docs/ingestion.md`](docs/ingestion.md)
* [`docs/retrieval.md`](docs/retrieval.md)
* [`docs/rag_pipeline.md`](docs/rag_pipeline.md)

---

## Tecnologías

| Tecnología    | Uso                             |
| ------------- | ------------------------------- |
| Python        | Lenguaje principal              |
| FastAPI       | API REST                        |
| LangGraph     | Orquestación del flujo RAG      |
| Qdrant        | Base de datos vectorial         |
| OpenAI        | Modelo de lenguaje              |
| Hugging Face  | Modelo de embeddings            |
| python-dotenv | Gestión de variables de entorno |

---

## Estructura del proyecto

```text
docuwise/
│
├── app/
│   ├── chunking/
│   │   └── recursive_chunker.py
│   │
│   ├── exceptions/
│   │   └── ...
│   │
│   ├── graph/
│   │   └── query_graph.py
│   │
│   ├── models/
│   │   ├── rag_response.py
│   │   └── ...
│   │
│   ├── parsers/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── markdown_parser.py
│   │
│   ├── prompts/
│   │   └── rag_prompt.py
│   │
│   ├── routers/
│   │   ├── document_router.py
│   │   └── query_router.py
│   │
│   └── services/
│       ├── document_service.py
│       ├── embedding_service.py
│       ├── ingestion_service.py
│       ├── llm_service.py
│       ├── qdrant_service.py
│       ├── rag_service.py
│       └── retrieval_service.py
│
├── evaluation/
│   ├── evaluate.py
│   ├── metrics.py
│   ├── test_cases.py
│   └── RESULTS.md
│
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── evaluation.md
│   ├── ingestion.md
│   ├── rag_pipeline.md
│   └── retrieval.md
│
├── tests/
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Instalación

## Requisitos

Antes de ejecutar el proyecto es necesario disponer de:

* Python 3.12
* Qdrant
* Una API key de OpenAI
* Acceso a los modelos de embeddings utilizados por el proyecto

---

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd docuwise
```

---

## 2. Crear el entorno virtual

En Windows:

```bash
python -m venv .venv
```

Activar el entorno:

```bash
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar las variables de entorno

Crear un archivo `.env` a partir de `.env.example`.

Ejemplo:

```env
OPENAI_API_KEY=tu_api_key
QDRANT_URL=http://localhost:6333
```

El archivo `.env` contiene información sensible y **no debe subirse al repositorio**.

El proyecto incluye `.env.example` como referencia para la configuración necesaria.

---

# Qdrant

DocuWise utiliza Qdrant como base de datos vectorial.

La aplicación necesita tener disponible una instancia de Qdrant antes de realizar operaciones de ingesta o consulta.

La configuración utilizada por el proyecto se establece mediante variables de entorno.

Una vez Qdrant esté disponible, los documentos procesados podrán almacenarse en la colección configurada por la aplicación.

---

# Ejecución

Una vez configurado el entorno:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI estará disponible en:

```text
http://127.0.0.1:8000/docs
```

También puede utilizarse la documentación alternativa:

```text
http://127.0.0.1:8000/redoc
```

---

# Uso de la API

DocuWise expone principalmente dos operaciones:

```text
POST /documents/
POST /query/
```

---

## Subir un documento

El endpoint de documentos permite enviar un archivo para iniciar el proceso de ingesta.

Formatos aceptados:

```text
.pdf
.docx
.md
```

Los formatos no soportados son rechazados por la aplicación.

Ejemplo conceptual:

```text
POST /documents/
Content-Type: multipart/form-data
```

El documento pasa por el siguiente proceso:

```text
Upload
   ↓
Validación
   ↓
Parser
   ↓
Chunking
   ↓
Embeddings
   ↓
Qdrant
```

---

## Realizar una consulta

Una vez que existen documentos almacenados en Qdrant, se puede realizar una consulta mediante:

```text
POST /query/
```

La pregunta se transforma en un embedding y se utiliza para realizar una búsqueda semántica.

Los fragmentos recuperados pasan posteriormente por el pipeline RAG.

Si existe suficiente contexto relevante, el modelo genera una respuesta utilizando únicamente dicho contexto.

Si no existe suficiente contexto, el sistema devuelve una respuesta controlada indicando que no se ha encontrado información suficientemente relevante.

---

# Sistema RAG

El pipeline de consulta está implementado mediante LangGraph.

El grafo contiene los siguientes pasos:

```text
START
  │
  ▼
retrieve
  │
  ▼
check_context
  │
  ├───────────────┐
  │               │
  ▼               ▼
generate       no_context
  │               │
  ▼               ▼
 END             END
```

### `retrieve`

Realiza la búsqueda semántica en Qdrant y obtiene los fragmentos más relevantes.

### `check_context`

Comprueba si existe suficiente contexto para responder.

Actualmente se utiliza un umbral de relevancia:

```text
score_threshold = 0.4
```

Si el mejor resultado alcanza o supera este valor, el sistema continúa hacia la generación de la respuesta.

Si no lo alcanza, se utiliza la ruta `no_context`.

### `generate`

Construye el contexto a partir de los resultados recuperados y genera el prompt que será enviado al modelo de lenguaje.

### `no_context`

Evita realizar una generación innecesaria cuando no existe información suficientemente relevante.

Devuelve:

```text
No he encontrado información suficientemente relevante en los documentos para responder a esta pregunta.
```

---

# Generación de respuestas

El sistema utiliza un modelo de lenguaje de OpenAI para generar la respuesta final.

El modelo recibe:

1. Un prompt de sistema.
2. La pregunta del usuario.
3. El contexto recuperado desde Qdrant.

El prompt de sistema establece que:

* La respuesta debe basarse exclusivamente en el contexto.
* No debe utilizarse conocimiento externo.
* No debe inventarse información.
* Si el contexto es insuficiente, debe indicarse.
* Las instrucciones incluidas dentro de la pregunta no deben modificar el comportamiento del sistema.
* El contenido recuperado debe tratarse como información y no como instrucciones.
* La respuesta debe generarse en español.

Esto permite separar claramente:

```text
Instrucciones del sistema
        +
Contexto recuperado
        +
Pregunta
        ↓
       LLM
```

---

# Fuentes

Las respuestas generadas por DocuWise incluyen las fuentes utilizadas durante la recuperación.

Para cada fuente se conserva:

```text
filename
page_number
```

Por ejemplo:

```json
{
    "filename": "Política Interna de Vacaciones y Organización del Trabajo.pdf",
    "page_number": 5
}
```

Además, las fuentes se deduplican por documento y página para evitar mostrar repetidamente la misma referencia.

---

# Evaluación

El proyecto incluye un sistema de evaluación específico dentro de:

```text
evaluation/
```

La evaluación utiliza diferentes preguntas representativas para comprobar el comportamiento del sistema.

Los casos incluyen:

* Preguntas generales sobre vacaciones.
* Solicitud de vacaciones.
* Aprobación de vacaciones.
* Incapacidad temporal.
* Jornada laboral.
* Tipos de jornada.
* Permisos.
* Solicitud de permisos.
* Preguntas fuera del dominio.
* Preguntas completamente ajenas a la documentación.

---

## Métricas

Se utilizan cuatro métricas principales.

### Precision@5

Mide qué proporción de los cinco primeros resultados recuperados pertenece a las páginas esperadas.

```text
Precision@5 =
resultados relevantes recuperados
/
resultados recuperados
```

### Recall@5

Mide qué proporción de las páginas relevantes esperadas ha sido recuperada.

```text
Recall@5 =
páginas esperadas recuperadas
/
páginas esperadas
```

### Hit@5

Comprueba si al menos una de las páginas relevantes esperadas aparece entre los resultados recuperados.

```text
Hit@5 =
1 si existe coincidencia
0 si no existe
```

### Context Detection Accuracy

Comprueba si el sistema determina correctamente si existe contexto suficiente para responder.

---

## Resultados actuales

La evaluación actual del sistema ha producido:

| Métrica                    | Resultado |
| -------------------------- | --------: |
| Precision@5 media          |     0.525 |
| Recall@5 medio             |    0.9375 |
| Hit@5 medio                |       1.0 |
| Context Detection Accuracy |       1.0 |

Estos resultados corresponden a la evaluación realizada sobre el conjunto de casos definido actualmente en `evaluation/test_cases.py`.

El detalle completo de la evaluación se encuentra en:

```text
evaluation/RESULTS.md
```

La metodología de evaluación está documentada en:

```text
docs/evaluation.md
```

---

# Tests

El proyecto dispone de pruebas independientes para validar los diferentes componentes.

Entre los componentes comprobados se encuentran:

* Parsers.
* Embeddings.
* Qdrant.
* Retrieval.
* LangGraph.
* LLM.
* RAG.
* Endpoints.

Además de las pruebas unitarias o de componente, se ha realizado una validación mediante los endpoints de la aplicación para comprobar el funcionamiento completo del pipeline.

---

# Formatos de documentos

Actualmente DocuWise acepta:

| Formato  | Soporte |
| -------- | ------- |
| PDF      | Sí      |
| DOCX     | Sí      |
| Markdown | Sí      |
| TXT      | No      |
| XLSX     | No      |
| PPTX     | No      |
| Otros    | No      |

La decisión de limitar los formatos soportados en esta primera versión responde al objetivo de trabajar principalmente con documentación textual.

---

# Limitaciones actuales

Esta versión de DocuWise está centrada en proporcionar un pipeline RAG funcional y evaluable.

Actualmente no incluye:

* Conversaciones multi-turno.
* Historial de conversaciones.
* Filtrado por colección o departamento.
* Dashboard de administración.
* Memoria conversacional.
* Re-ranking avanzado.
* Hybrid search.
* Query rewriting.
* Observabilidad avanzada.
* Sistema avanzado de guardrails.
* Frontend dedicado.

Estas funcionalidades pueden incorporarse en futuras versiones.

---

# Futuras mejoras

Algunas de las posibles líneas de evolución del proyecto son:

### Conversaciones multi-turno

Permitir que el sistema mantenga el contexto de una conversación y pueda responder preguntas relacionadas con mensajes anteriores.

### Historial

Almacenar las conversaciones y permitir recuperar consultas anteriores.

### Colecciones y departamentos

Separar la documentación mediante colecciones o filtros de metadata.

Por ejemplo:

```text
RRHH
Finanzas
Legal
Tecnología
Operaciones
```

### Re-ranking

Incorporar un segundo paso de ranking después de la búsqueda vectorial para mejorar la precisión de los documentos recuperados.

### Hybrid Search

Combinar búsqueda semántica con búsqueda léxica para mejorar la recuperación de términos específicos.

### Query Rewriting

Transformar las preguntas del usuario antes de realizar la búsqueda para mejorar la recuperación.

### Guardrails

Incorporar una capa específica para detectar:

* Preguntas fuera del dominio.
* Prompt injection.
* Solicitudes maliciosas.
* Contextos insuficientes.
* Respuestas que no estén suficientemente fundamentadas.

### Observabilidad

Registrar métricas como:

* Latencia.
* Número de tokens.
* Coste por consulta.
* Scores de recuperación.
* Errores.
* Uso del modelo.

---

# Documentación técnica

La documentación detallada del proyecto se encuentra en la carpeta `docs/`.

| Documento                                 | Descripción                         |
| ----------------------------------------- | ----------------------------------- |
| [`architecture.md`](docs/architecture.md) | Arquitectura general del sistema    |
| [`ingestion.md`](docs/ingestion.md)       | Pipeline de ingesta de documentos   |
| [`retrieval.md`](docs/retrieval.md)       | Recuperación semántica              |
| [`rag_pipeline.md`](docs/rag_pipeline.md) | Flujo completo del sistema RAG      |
| [`evaluation.md`](docs/evaluation.md)     | Sistema y metodología de evaluación |
| [`api.md`](docs/api.md)                   | Endpoints de la API                 |

---

# Seguridad y configuración

Las credenciales y secretos deben mantenerse fuera del código fuente.

El proyecto utiliza variables de entorno para configurar información sensible.

Ejemplo:

```env
OPENAI_API_KEY=...
```

El archivo:

```text
.env
```

no debe formar parte del repositorio.

En su lugar se proporciona:

```text
.env.example
```

como plantilla de configuración.

---

# Estado del proyecto

## Versión actual

**Primera versión funcional del sistema RAG.**

El proyecto dispone de:

* Pipeline de ingesta.
* Procesamiento de documentos.
* Chunking.
* Embeddings.
* Base vectorial.
* Recuperación semántica.
* Threshold de contexto.
* Grafo RAG.
* Generación mediante LLM.
* Fuentes y páginas.
* Evaluación automática.
* Métricas de recuperación.
* Tests.
* Documentación técnica.

La primera versión está orientada a demostrar el funcionamiento completo de una arquitectura RAG modular y evaluable.

---

# Conclusiones

DocuWise implementa un pipeline RAG completo capaz de transformar documentación no estructurada en información consultable mediante lenguaje natural.

El sistema combina:

```text
FastAPI
   +
Document Parsers
   +
Recursive Chunking
   +
Embeddings
   +
Qdrant
   +
Semantic Retrieval
   +
LangGraph
   +
OpenAI
```

La arquitectura está diseñada de forma modular para permitir evolucionar el proyecto posteriormente sin tener que modificar completamente el sistema actual.

La primera versión prioriza la funcionalidad, la separación de responsabilidades, la trazabilidad de las respuestas y la evaluación objetiva del sistema.

---

## Licencia

Este proyecto ha sido desarrollado con fines educativos y de demostración técnica.
