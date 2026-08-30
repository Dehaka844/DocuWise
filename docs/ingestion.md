# Ingestión de documentos

## Visión general

El proceso de ingestión es responsable de transformar un documento proporcionado por el usuario en información que pueda ser utilizada posteriormente por el sistema RAG.

El objetivo final del proceso es almacenar fragmentos semánticamente representativos del documento dentro de la base de datos vectorial Qdrant.

El pipeline completo de ingestión es el siguiente:

```text
UploadFile
    ↓
Validación del formato
    ↓
Parser correspondiente
    ↓
ParsedDocument
    ↓
Chunking
    ↓
DocumentChunk
    ↓
Generación de embeddings
    ↓
Almacenamiento en Qdrant
```

Cada una de estas etapas tiene una responsabilidad independiente.

---

# Entrada del documento

Los documentos se reciben a través de FastAPI utilizando el tipo:

```python
UploadFile
```

Este tipo permite trabajar con archivos subidos mediante peticiones HTTP sin necesidad de cargar manualmente el archivo completo desde una ruta local.

El sistema valida el formato del archivo antes de continuar con su procesamiento.

Actualmente, DocuWise acepta los siguientes formatos:

* `.pdf`
* `.docx`
* `.md`

Los formatos no soportados son rechazados por el sistema.

Por ejemplo, un archivo `.txt` no se procesa actualmente, aunque podría añadirse soporte en el futuro mediante la implementación de un parser adicional.

---

# Parser de documentos

Después de validar el formato, el documento se procesa utilizando el parser correspondiente.

Los parsers se encuentran dentro del módulo:

```text
app/ingestion/parsers/
```

La responsabilidad de un parser es extraer el contenido del documento y convertirlo a una estructura común.

Esto permite que las siguientes etapas del pipeline no dependan del formato original del archivo.

Por ejemplo, un documento PDF y un documento DOCX pueden tener mecanismos internos de extracción completamente diferentes, pero ambos deben producir una representación común del contenido.

---

# Procesamiento asíncrono

Los parsers de DocuWise pueden utilizar procesamiento asíncrono.

Por este motivo, el procesamiento de documentos se realiza utilizando `await`.

Un flujo simplificado sería:

```python
document = await parser.parse(file)
```

Esto permite que el endpoint de subida trabaje correctamente con operaciones de procesamiento que requieren un flujo asíncrono.

---

# ParsedDocument

Independientemente del formato original del archivo, el resultado del proceso de parsing se representa mediante `ParsedDocument`.

La estructura principal es:

```python
class PageContent(BaseModel):

    page_number: int

    content: str


class ParsedDocument(BaseModel):

    pages: list[PageContent]

    metadata: dict[str, Any]
```

`ParsedDocument` contiene dos elementos principales:

* `pages`
* `metadata`

---

# PageContent

Cada elemento de `pages` representa una unidad de contenido del documento.

Su estructura es:

```python
class PageContent(BaseModel):

    page_number: int

    content: str
```

Cada objeto contiene:

* `page_number`: número de página o identificador de la sección.
* `content`: contenido textual extraído.

El uso de una estructura común permite mantener información sobre el origen del contenido durante las siguientes etapas del pipeline.

---

# Metadata del documento

Además del contenido, el documento puede contener metadata asociada.

La metadata se representa mediante:

```python
metadata: dict[str, Any]
```

Esto permite almacenar información adicional sin limitar la estructura a un conjunto fijo de campos.

Actualmente, la metadata puede incluir información como:

* Nombre del archivo.
* Tipo de documento.
* Número total de páginas.

La metadata del documento se propaga posteriormente a los chunks generados.

Esto permite conservar la trazabilidad del contenido original.

---

# Chunking

Una vez que el documento ha sido procesado, su contenido se divide en fragmentos más pequeños.

Esta responsabilidad corresponde a:

```text
RecursiveChunker
```

El objetivo del chunking es evitar almacenar documentos completos como una única unidad.

En su lugar, el contenido se divide en fragmentos que pueden representar unidades semánticas más pequeñas.

El flujo es:

```text
ParsedDocument
    ↓
RecursiveChunker
    ↓
DocumentChunk
```

Cada página puede generar uno o varios chunks.

---

# DocumentChunk

Los fragmentos generados se representan mediante:

```python
class DocumentChunk(BaseModel):

    content: str

    metadata: dict[str, Any]
```

Cada `DocumentChunk` contiene:

* `content`: texto del fragmento.
* `metadata`: información sobre el origen del fragmento.

Un chunk se crea utilizando una estructura similar a:

```python
DocumentChunk(
    content=content,
    metadata={
        **document.metadata,
        "page_number": page.page_number,
        "chunk_index": chunk_index,
    },
)
```

La expresión:

```python
**document.metadata
```

permite conservar toda la metadata original del documento.

Después se añade información específica del chunk:

```text
page_number
chunk_index
```

De esta forma, cada fragmento mantiene información sobre:

* El documento original.
* El número de página.
* La posición del chunk dentro del proceso de división.

---

# Importancia del tamaño de los chunks

El tamaño de los chunks es una decisión importante dentro de un sistema RAG.

Si los chunks son demasiado grandes:

* Pueden contener información no relacionada.
* La recuperación puede ser menos precisa.
* Se puede enviar demasiado contexto al modelo de lenguaje.

Si son demasiado pequeños:

* Puede perderse información necesaria para comprender el contenido.
* La información relevante puede quedar dividida entre múltiples chunks.

El objetivo es encontrar un equilibrio entre:

```text
Contexto suficiente
+
Unidad semántica
+
Precisión en recuperación
```

El `RecursiveChunker` permite dividir progresivamente el contenido utilizando separadores, intentando mantener fragmentos con sentido semántico.

---

# Generación de embeddings

Después de generar los chunks, su contenido se convierte en embeddings.

Esta responsabilidad corresponde a:

```text
EmbeddingService
```

El servicio proporciona dos métodos principales:

```python
embed_text()
```

y:

```python
embed_texts()
```

El primer método genera el embedding de un único texto.

El segundo permite procesar múltiples textos.

Para la ingestión de documentos se utiliza el procesamiento de múltiples textos.

El flujo es:

```text
DocumentChunks
    ↓
Extracción del contenido
    ↓
Lista de textos
    ↓
embed_texts()
    ↓
Embeddings
```

Por ejemplo:

```python
texts = [
    chunk.content
    for chunk in chunks
]

embeddings = embedding_service.embed_texts(texts)
```

---

# Dimensiones de los embeddings

Los embeddings generados por el modelo utilizado actualmente tienen:

```text
384 dimensiones
```

Cada fragmento de texto se representa mediante un vector de números de esta longitud.

Por ejemplo:

```text
[
    0.1718,
    -0.0603,
    0.0675,
    ...
]
```

El embedding no representa palabras individuales de forma directa.

Representa el significado semántico del contenido mediante una posición dentro de un espacio vectorial.

Textos con significados similares tienden a generar vectores cercanos dentro de este espacio.

Esto permite realizar búsquedas semánticas.

---

# Procesamiento por lotes

`EmbeddingService` permite procesar múltiples textos mediante batches.

Esto evita generar embeddings realizando una llamada individual para cada chunk.

El flujo es:

```text
Chunks
    ↓
Lista de textos
    ↓
Batch 1
Batch 2
Batch 3
    ↓
Embeddings finales
```

El uso de batches permite:

* Procesar múltiples chunks de manera más eficiente.
* Reducir el número de operaciones individuales.
* Facilitar el procesamiento de documentos grandes.

---

# Validación de la ingestión

Durante el proceso de ingestión, es importante mantener la correspondencia entre:

```text
Número de chunks
=
Número de embeddings
```

Cada chunk debe tener exactamente un embedding asociado.

Por ejemplo:

```text
Número de chunks: 58
Número de embeddings: 58
Dimensiones del primer embedding: 384
```

Esta validación permite comprobar que todos los fragmentos del documento han sido correctamente vectorizados.

---

# Almacenamiento en Qdrant

Después de generar los embeddings, los chunks y sus vectores se almacenan en Qdrant.

La operación de almacenamiento se realiza mediante:

```text
QdrantService
```

Cada chunk se almacena junto con:

* Su embedding.
* Su contenido.
* La metadata necesaria para identificar su origen.

Un punto almacenado en Qdrant contiene conceptualmente:

```text
ID
+
Vector
+
Payload
```

El payload contiene información asociada al chunk.

Una estructura simplificada sería:

```python
{
    "content": chunk.content,
    "filename": filename,
    "source_type": source_type,
    "page_number": chunk.metadata["page_number"],
    "chunk_index": chunk.metadata["chunk_index"],
}
```

También pueden conservarse otros datos procedentes de la metadata original, como el número total de páginas.

---

# Ejemplo de información almacenada

Un chunk almacenado en Qdrant puede tener una estructura conceptual como:

```text
ID:
011dd28f-5bac-4710-8f2a-0d729fd75a11

Payload:
{
    "content": "...",
    "filename": "documento.pdf",
    "source_type": "pdf",
    "page_count": 22,
    "page_number": 4,
    "chunk_index": 11
}

Vector:
[
    -0.011888737,
    0.06627152,
    -0.03852355,
    ...
]
```

Esta información permite posteriormente recuperar tanto el vector como el contenido y su origen.

---

# IngestionService

La coordinación del proceso de ingestión se realiza mediante:

```text
IngestionService
```

Este servicio conecta los principales componentes del pipeline:

```text
RecursiveChunker
+
EmbeddingService
+
QdrantService
```

La responsabilidad de este servicio es coordinar el flujo completo desde los chunks hasta su almacenamiento vectorial.

La separación mediante servicios permite evitar que los endpoints contengan directamente la lógica de:

* Chunking.
* Generación de embeddings.
* Indexación en Qdrant.

---

# Flujo completo de ingestión

El proceso completo puede resumirse de la siguiente forma:

```text
Usuario
    ↓
Subida de documento
    ↓
FastAPI
    ↓
Validación del formato
    ↓
Parser
    ↓
ParsedDocument
    ↓
Pages
    ↓
RecursiveChunker
    ↓
DocumentChunks
    ↓
EmbeddingService
    ↓
Vectores de 384 dimensiones
    ↓
QdrantService
    ↓
Collection de Qdrant
```

Una vez finalizado este proceso, el documento queda disponible para consultas semánticas.

---

# Resultado del proceso

Como resultado de la ingestión, cada documento queda representado por múltiples chunks.

Cada chunk dispone de:

* Contenido textual.
* Un embedding de 384 dimensiones.
* Metadata sobre su origen.

Esto permite que el sistema pueda responder posteriormente a preguntas relacionadas con partes específicas del documento sin necesidad de enviar el documento completo al modelo de lenguaje.

La información se recupera dinámicamente utilizando búsqueda semántica.

---

# Principios del pipeline de ingestión

El proceso de ingestión sigue varios principios:

## Normalización

Todos los formatos de documento terminan convertidos a una estructura común.

```text
PDF ────┐
        │
DOCX ───┼──→ ParsedDocument
        │
MD ─────┘
```

## Trazabilidad

Cada chunk mantiene información sobre el documento del que procede.

## Modularidad

Los parsers, el chunking, los embeddings y el almacenamiento se mantienen como componentes independientes.

## Eficiencia

La generación de embeddings permite procesar múltiples textos en batches.

## Consistencia

Todos los vectores almacenados tienen la misma dimensionalidad:

```text
384 dimensiones
```

---

# Próximos pasos

Una vez que el documento ha sido procesado y almacenado en Qdrant, puede utilizarse durante el proceso de consulta.

La siguiente fase del sistema es la recuperación semántica.

Este proceso se documenta en:

```text
docs/retrieval.md
```

El flujo será:

```text
Pregunta del usuario
    ↓
Embedding de la pregunta
    ↓
Búsqueda vectorial en Qdrant
    ↓
Resultados ordenados por similitud
    ↓
Fragmentos recuperados
```
