# Arquitectura de DocuWise 2.0

DocuWise combina una aplicación web y API FastAPI con PostgreSQL, Qdrant, un modelo local de embeddings y un LLM de OpenAI.

## Componentes

```text
Frontend estático ──HTTP/JWT──> FastAPI
                                  ├── PostgreSQL
                                  │   ├── usuarios, roles y departamentos
                                  │   ├── conversaciones y mensajes
                                  │   └── fuentes asociadas a respuestas
                                  ├── Qdrant
                                  │   └── chunks, embeddings y ACL metadata
                                  ├── Sentence Transformers
                                  └── OpenAI Responses API
```

- `app/api/routes/`: endpoints de documentos, búsqueda y consulta RAG.
- `app/database_routers/`: autenticación, conversaciones, mensajes y administración de usuarios.
- `app/database_models/`, `app/database_services/`: persistencia y reglas de negocio de PostgreSQL.
- `app/ingestion/` y `app/chunking/`: parsing y división de documentos.
- `app/services/`: embeddings, recuperación, Qdrant, ingesta y llamadas al LLM.
- `app/graph/` y `app/prompts/`: flujo LangGraph y prompts.
- `frontend/`: HTML, TypeScript/JavaScript compilado, Sass/CSS.

## Datos

PostgreSQL guarda cuentas, su rol (`user`/`admin`), departamentos, conversaciones, mensajes y fuentes de mensajes. Las tablas se administran con Alembic.

Qdrant usa la colección `document_chunks`, vectores de 384 dimensiones y distancia coseno. Cada payload contiene el contenido y metadata como nombre y tipo de archivo, página cuando aplica, índice de chunk, dominios, visibilidad, departamentos autorizados y propietarios autorizados.

## Seguridad de acceso

Las rutas privadas validan el token JWT. Los endpoints de RAG pasan identidad, departamentos y rol a Qdrant. Los usuarios ven documentos generales, documentos autorizados a sus departamentos y documentos personales propios. El administrador omite el filtro de documentos. La subida/borrado documental y la gestión administrativa de usuarios requieren rol `admin` en backend.

## Servicios locales

`docker-compose.yml` inicia Qdrant y PostgreSQL. FastAPI se inicia por separado con Uvicorn y sirve el frontend bajo `/frontend`. La configuración de conexión se lee de variables de entorno; consulta `.env.example`.

## Recorrido de una petición de chat

1. El frontend envía un mensaje a `/conversations/{id}/messages` con el token Bearer.
2. FastAPI comprueba que la conversación pertenezca al usuario y carga hasta diez mensajes anteriores.
3. El mensaje de usuario se guarda en PostgreSQL.
4. `RAGService` crea el grafo y pasa la pregunta, historial, ID, departamentos y rol al pipeline.
5. Qdrant filtra los puntos por permisos antes de devolver resultados.
6. El grafo selecciona fragmentos relevantes y llama al modelo cuando hay contexto suficiente.
7. La respuesta y sus fuentes se persisten en PostgreSQL y vuelven al navegador.

## Recorrido de subida

La ruta `/documents/` requiere un administrador. Valida visibilidad, departamentos y propietario; deriva los ámbitos del documento; después el parser y el chunker preparan los textos, el servicio de embeddings genera un vector por chunk y Qdrant guarda cada punto con su payload. La base de datos relacional no almacena el archivo ni los vectores.

## Separación de responsabilidades

| Módulo | Responsabilidad principal |
|---|---|
| `app/api/routes` | API de documentos, búsqueda y consulta directa |
| `app/database_routers` | Registro/login, conversaciones/mensajes y administración |
| `app/database_services` | Reglas relacionales, tokens, contraseñas, usuarios y conversaciones |
| `app/ingestion/parsers` | Conversión PDF, DOCX y MD a texto estructurado |
| `app/chunking` | División del texto y propagación de metadata |
| `app/services/embedding_service.py` | Codificación de texto con Sentence Transformers |
| `app/services/qdrant_service.py` | Crear colección, upsert, búsqueda con filtro ACL y borrado |
| `app/graph/query_graph.py` | Estado, enrutamiento, filtrado por score, prompts, respuesta y fuentes |
| `app/services/llm_service.py` | Reformulación y generación mediante OpenAI Responses API |
| `app/prompts/rag_prompt.py` | Reglas comunes, módulos por ámbito y prompt de reformulación |

## Configuración y arranque

`app/main.py` carga `.env`, monta los recursos estáticos y registra routers. Qdrant se configura con `QDRANT_HOST`/`QDRANT_PORT`; PostgreSQL con `POSTGRES_*`; JWT con `JWT_*`; OpenAI con `OPENAI_API_KEY`. Las tablas se versionan con Alembic. La colección de Qdrant se crea al primer upsert si todavía no existe.

El endpoint `/health` comprueba Qdrant de forma básica; no realiza una prueba integral de todos los componentes ni sustituye una monitorización de producción.
