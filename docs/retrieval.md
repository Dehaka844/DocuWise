# Recuperación y permisos

## Búsqueda

`EmbeddingService` usa `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, genera vectores normalizados de 384 dimensiones y codifica preguntas y chunks con el mismo modelo. `QdrantService` busca en la colección `document_chunks` mediante distancia coseno.

La API acepta `limit` entre 1 y 20; el valor por defecto es 5. El umbral usado por `QueryGraph` para considerar un fragmento relevante es `0.4`. Es un valor fijo del código actual y debe tratarse como una configuración pendiente de evaluación, no como una garantía universal de relevancia.

## Filtro de acceso en Qdrant

El filtro se aplica antes de devolver resultados:

- Usuarios normales: `visibility=all` **o** coincidencia con alguno de sus departamentos **o** coincidencia con su `user_id` como propietario.
- Administradores: sin filtro de acceso documental.

El rol y la pertenencia a departamentos son conceptos distintos: el rol define permisos administrativos y los departamentos autorizan colecciones de documentos.

## Contexto y fuentes

El grafo conserva para la generación únicamente los resultados con `score >= 0.4`; la detección de contexto, el prompt por ámbitos y las fuentes usan ese mismo conjunto. Las fuentes se deduplican por archivo y página. En PDF se devuelve la página; para DOCX y Markdown se devuelve solo el nombre del documento porque no se conoce su paginación física.

El filtrado por score reduce coincidencias débiles, pero no garantiza que todos los fragmentos restantes contesten la pregunta. La evaluación manual de `informes/` aún muestra fuentes irrelevantes y mezcla de documentos; el umbral y la estrategia de ranking requieren evaluación adicional.

## API de búsqueda frente a respuesta RAG

`POST /search/` es una herramienta de inspección: devuelve los resultados y scores de la búsqueda para el usuario autenticado. No aplica la generación de respuesta. `POST /query/` usa el mismo servicio de recuperación y añade detección de contexto, selección de ámbitos y generación. En el chat, los mismos permisos se derivan de la cuenta y se pasan desde el router de mensajes.

La distancia coseno produce un score ordenable, pero el score no es una probabilidad de que la respuesta sea correcta. Un resultado sobre `0.4` puede ser temáticamente parecido y aun así pertenecer a otro documento o no contener el dato preguntado. Por ejemplo, dos proyectos con métricas de piloto pueden recuperar fragmentos similares.

## Qué controla cada parámetro

- `limit`: número máximo de candidatos solicitados a Qdrant, de 1 a 20; valor por defecto 5.
- `score_threshold`: criterio binario usado por `QueryGraph` para incluir un resultado en la generación y considerar que hay contexto. Actualmente vale 0.4.
- `domains`: metadata del documento que selecciona instrucciones de estilo. No es un filtro de consulta y no identifica por sí sola qué documento nombra el usuario.
- `visibility`, `allowed_departments`, `allowed_user_ids`: filtro de autorización en Qdrant, aplicado antes de devolver candidatos.

No hay reranker ni búsqueda híbrida implementados actualmente. La búsqueda es densa/vectorial. Ajustar `limit` o el umbral debe hacerse midiendo el mismo conjunto de casos de evaluación, porque un límite mayor puede recuperar evidencia adicional y también más fragmentos distractores.

## Fuentes

Las fuentes se deduplican por archivo y página en PDF. En DOCX/Markdown la página es nula y se deduplican por archivo, lo cual significa que la interfaz no permite inspeccionar qué chunk concreto de ese documento se usó. Para mejorar trazabilidad se podría añadir un identificador de chunk/sección a las fuentes, sin confundirlo con una cita por página.
