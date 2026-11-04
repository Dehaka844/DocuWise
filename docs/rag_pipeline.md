# Pipeline RAG

El pipeline se implementa en `QueryGraph` mediante LangGraph.

```text
rewrite_query → retrieve → check_context
                              ├─ relevante: generate → END
                              └─ insuficiente: no_context → END
```

## Reformulación

Cuando existe historial, `LLMService.rewrite_query` intenta convertir la pregunta actual en una consulta autónoma. El historial solo ayuda a resolver referencias; no se considera fuente documental. Si falla la llamada de reformulación, se utiliza la pregunta original. Sin historial, no se realiza esa llamada adicional.

## Recuperación y contexto

La consulta se vectoriza y se busca en Qdrant aplicando el filtro de acceso del usuario. Por defecto se solicitan cinco resultados, con máximo 20. Si ninguno supera `score_threshold=0.4`, el grafo devuelve el mensaje de contexto insuficiente sin llamar al LLM de respuesta.

Si hay resultados sobre el umbral, esos mismos fragmentos forman el contexto, determinan los ámbitos del prompt y producen las fuentes. Los demás resultados no se incluyen en la respuesta generada.

## Prompt y generación

`build_rag_system_prompt` concatena las reglas comunes con módulos de los ámbitos encontrados en la metadata de los fragmentos relevantes: general, RR. HH., datos personales, técnico y marketing. Los módulos orientan el estilo; no imponen una plantilla rígida. Los ámbitos personales limitan la información personal que se debe revelar.

`RAG_USER_PROMPT` incluye historial de conversación, contexto documental y pregunta original. `LLMService` envía ambos prompts a OpenAI. Las respuestas y fuentes se guardan asociadas a mensajes en PostgreSQL.

## Conversación

La API de mensajes carga hasta diez mensajes anteriores de la conversación para reformular preguntas relacionadas y dar contexto conversacional. El acceso a cada conversación se limita a su propietario.

## Estado de `QueryGraph`

Durante una invocación, LangGraph transporta un estado con campos conceptuales como:

| Campo | Contenido |
|---|---|
| `query` | Pregunta original que recibirá el LLM de respuesta |
| `search_query` | Consulta usada en retrieval; puede ser reformulada |
| `limit` | Máximo de resultados solicitados a Qdrant |
| `conversation_history` | Mensajes anteriores disponibles para la conversación |
| `user_id`, `departments`, `is_admin` | Identidad y permisos aplicados a la búsqueda |
| `results` | Resultados Qdrant con contenido, score y metadata |
| `has_sufficient_context` | Si quedó al menos un resultado sobre el umbral |
| `answer`, `sources` | Respuesta final y fuentes deduplicadas |

## Nodos del grafo

### `rewrite_query`

Sin historial, establece `search_query` igual a la pregunta original. Con historial, llama a `LLMService.rewrite_query()` para resolver referencias como “eso” o “¿y ese caso?”. Si OpenAI devuelve error o una salida vacía, se usa la pregunta original. Esta llamada solo se ejecuta en conversaciones que ya tienen mensajes anteriores.

### `retrieve`

Genera el embedding de `search_query` y consulta Qdrant con `limit` e información de acceso. Qdrant devuelve resultados ordenados por score.

### `check_context` y `route_context`

`_relevant_results()` selecciona los resultados con score mayor o igual a 0.4. Si la selección queda vacía, la ruta salta a `no_context`; no se envía contexto vacío al LLM.

### `no_context`

Devuelve el mensaje fijo de falta de información y `sources=[]`. No realiza la llamada de generación. `has_sufficient_context` queda falso.

### `generate`

Une el contenido de resultados relevantes, toma de su metadata los ámbitos presentes, construye el prompt de sistema, serializa el historial y llama una vez al LLM de respuesta. Las fuentes se construyen de los mismos resultados, agrupadas por filename/página; las fuentes no PDF no prometen página.

## Composición del prompt

El prompt general establece la fidelidad documental, la respuesta en español, la resistencia a instrucciones dentro del contexto y el estilo de respuesta directa. Sobre él se añaden módulos de los ámbitos que aparezcan en los fragmentos relevantes:

| Ámbito | Orientación |
|---|---|
| `general` | Breve y directo |
| `rrhh` | Procedimientos, requisitos, plazos y excepciones documentados |
| `datos_personales` | Minimizar datos personales y no inferir periodos/conceptos |
| `tecnico` | Explicación operativa y pasos ordenados cuando corresponda |
| `marketing` | Mensajes claros, sin promesas ni cifras no respaldadas |

Los módulos se concatenan en una sola llamada de generación; no existe un clasificador LLM intermedio ni una llamada separada por cada ámbito. Si se recuperan fragmentos de varios ámbitos, sus instrucciones se combinan. Esto orienta el estilo, pero no establece todavía una plantilla fija por ámbito.

## Persistencia del chat

El router guarda primero el mensaje del usuario, carga el historial anterior y luego ejecuta RAG. Al finalizar, almacena el mensaje del asistente y las fuentes en `message_sources`. Los borrados de conversación se propagan a sus mensajes y fuentes mediante la relación/cascada de base de datos.

## Límites conocidos

- El filtro de score no sustituye un reranker: resultados irrelevantes pueden superar 0.4.
- La similitud por tema puede traer fragmentos de dos proyectos distintos.
- El contexto se construye con todos los resultados que pasan el umbral y caben en el límite solicitado.
- Para DOCX/Markdown se conoce el archivo, pero no la página o el chunk visible en la interfaz.
- Los prompts de ámbito son instrucciones de estilo y privacidad, no validadores automáticos de hechos.
