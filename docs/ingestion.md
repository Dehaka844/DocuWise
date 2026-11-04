# Ingesta de documentos

## Flujo

```text
Subida autorizada de admin
  → selección del parser por extensión
  → extracción de texto y metadata
  → chunks de 1.000 caracteres con solapamiento de 200
  → embeddings normalizados de 384 dimensiones
  → puntos en Qdrant
```

Los formatos admitidos son PDF, DOCX y Markdown (`.md`). Los demás reciben un error de formato no soportado.

## Parsers y fuentes

- **PDF:** PyMuPDF extrae texto página a página. Las fuentes pueden señalar número de página.
- **DOCX:** `python-docx` recorre párrafos y tablas en su orden dentro del documento. Las tablas se convierten en texto que asocia los valores con las celdas de la primera fila, tratada como encabezado. `python-docx` no proporciona paginación renderizada; la fuente se muestra por nombre de documento, sin página.
- **Markdown:** el texto se procesa como un documento lógico; la fuente se muestra por nombre de archivo, sin página física.

El chunker divide cada página PDF por separado. DOCX y Markdown se representan como una unidad textual y pueden producir varios chunks. El `page_number=1` interno de esos parsers no representa una página física y no se muestra como tal.

## Metadata y permisos

Cada chunk hereda metadata documental y añade `page_number` y `chunk_index`. La API de subida agrega:

| Campo | Uso |
|---|---|
| `filename`, `source_type`, `page_count` | Procedencia del documento |
| `document_id`, `chunk_index` | Identificación lógica y posición del chunk |
| `domains` | `general`, `rrhh`, `tecnico`, `marketing`, `datos_personales` |
| `visibility` | `all`, `departments` o `personal` |
| `allowed_departments` | Departamentos autorizados |
| `allowed_user_ids` | Propietario autorizado para documentos personales |

Los ámbitos se derivan de la visibilidad y los departamentos seleccionados. No se permite que un usuario normal suba documentos.

## Actualizar un documento indexado

Subir de nuevo un archivo con el mismo nombre agrega nuevos puntos; no reemplaza automáticamente los anteriores. Para reindexar, elimina primero el archivo anterior como administrador y vuelve a subirlo. El endpoint de borrado elimina todos los puntos cuyo `filename` coincida exactamente, así que conviene mantener nombres únicos.

## Ejemplo de payload

Un punto indexado tiene un vector y un payload similar a este:

```json
{
  "content": "Texto recuperable del fragmento...",
  "filename": "Guia_RRHH.pdf",
  "source_type": "pdf",
  "page_count": 12,
  "page_number": 4,
  "chunk_index": 7,
  "document_id": "<uuid-del-documento>",
  "domains": ["rrhh"],
  "visibility": "departments",
  "allowed_departments": ["rrhh"],
  "allowed_user_ids": []
}
```

La metadata administrativa se replica en todos los chunks del archivo, de modo que Qdrant puede aplicar el filtro de acceso directamente en la búsqueda. `document_id` agrupa los puntos creados en una carga; el borrado implementado actualmente usa `filename`.

## Chunking actual

`RecursiveChunker` usa valores por defecto de 1.000 caracteres y 200 caracteres de solapamiento. Intenta cortar por párrafos (`\n\n`), líneas (`\n`) y espacios antes de recurrir a cortes por caracteres. El procesamiento ocurre por unidad de página entregada por el parser, de forma que un chunk PDF no cruza de una página a otra.

Los valores se miden en caracteres, no tokens. El solapamiento busca conservar contexto en los límites, pero no garantiza que títulos, tablas extensas o relaciones entre filas queden siempre en el mismo chunk; es una de las variables que conviene evaluar con casos concretos.

## DOCX y estructura de tablas

El parser usa `iter_inner_content()` para recorrer párrafos y tablas en el orden del documento. En una tabla:

1. Extrae texto de las celdas, también de párrafos y tablas anidados.
2. Usa la primera fila como encabezados.
3. Escribe cada fila posterior como pares `encabezado: valor`, facilitando la asociación semántica.

La paginación de DOCX depende del motor de renderizado y `python-docx` no la calcula. Por eso se devuelve la fuente sin página, aunque el parser mantenga una unidad lógica interna. Markdown también se trata como documento completo sin paginación física.

## Embeddings y almacenamiento

`EmbeddingService.embed_texts()` procesa los chunks en lotes de 32 por defecto, comprueba que no haya textos vacíos y normaliza los vectores. `QdrantService.upsert_chunks()` valida que exista un embedding por chunk, crea UUIDs nuevos y guarda contenido más metadata. La colección `document_chunks` usa distancia coseno y dimensión 384; modificar el modelo o dimensión requiere coordinar la configuración de Qdrant y reindexar el corpus.

## Al volver a indexar

Para que un cambio de parser se aplique a contenido ya cargado, hay que sustituir los puntos viejos:

1. Eliminar el archivo en el panel administrativo usando su filename exacto.
2. Subir de nuevo el archivo con visibilidad, departamentos y propietario correctos.
3. Comprobar el número de chunks y realizar consultas que dependan del texto recién extraído.
