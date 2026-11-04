# API de DocuWise

FastAPI genera la documentación interactiva en `/docs` y `/redoc`. Salvo registro, login y health, las rutas requieren `Authorization: Bearer <token>`. Las rutas administrativas requieren además rol `admin`.

## Autenticación

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /auth/register` | Público | Registra una cuenta con rol `user` |
| `POST /auth/login` | Público | Devuelve token Bearer y datos del usuario |
| `GET /auth/me` | Usuario | Devuelve la cuenta autenticada |

## Documentos

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /documents/` | Admin | Sube PDF, DOCX o MD mediante `multipart/form-data` |
| `DELETE /documents/?filename=<nombre.ext>` | Admin | Elimina todos los chunks con el nombre exacto |

Campos de subida: `file`, `visibility` (`all`, `departments`, `personal`), `allowed_departments` (campo repetido) y `owner_user_id` opcional para propietario. La visibilidad general no requiere departamento; `departments` exige al menos uno; `personal` exige propietario.

La respuesta de subida incluye `filename`, `chunk_count`, `embedding_count` y `stored_points`.

## Búsqueda y consulta

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /search/` | Usuario | Devuelve fragmentos y scores recuperados |
| `POST /query/` | Usuario | Ejecuta el pipeline RAG y devuelve respuesta, fuentes y `has_sufficient_context` |

Ambos reciben JSON con `query` y `limit` opcional (1–20, por defecto 5). Las rutas de conversación reciben `content` (1–5.000 caracteres) y `limit` con los mismos límites.

## Conversaciones y mensajes

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /conversations/` | Usuario | Crea conversación propia |
| `GET /conversations/` | Usuario | Lista conversaciones propias |
| `GET /conversations/{id}` | Propietario | Consulta una conversación |
| `PATCH /conversations/{id}` | Propietario | Cambia el título |
| `DELETE /conversations/{id}` | Propietario | Elimina conversación y mensajes |
| `GET /conversations/{id}/messages` | Propietario | Lista mensajes y fuentes |
| `POST /conversations/{id}/messages` | Propietario | Guarda pregunta, ejecuta RAG y guarda respuesta/fuentes |

## Administración de usuarios

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `GET /admin/users/` | Admin | Lista usuarios |
| `POST /admin/users/` | Admin | Crea usuario |
| `PATCH /admin/users/{id}` | Admin | Cambia rol, estado activo y/o departamentos |
| `DELETE /admin/users/{id}` | Admin | Elimina usuario |

El backend impide que el administrador se elimine o desactive a sí mismo y que se elimine/desactive al último administrador activo.

## Estado

`GET /health` devuelve el estado básico de la aplicación y de la conexión con Qdrant. No es una comprobación integral de PostgreSQL ni del servicio OpenAI.

## Envío de credenciales

Tras iniciar sesión, el cliente usa el token que devuelve `/auth/login` en las peticiones privadas:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

La contraseña nunca forma parte del token ni se devuelve en las respuestas. Las dependencias de autenticación comprueban la validez del token y que la cuenta siga activa; las rutas de administración comprueban además el rol actual en la base de datos.

## Ejemplos de petición

### Registro y login

```json
POST /auth/register
{
  "name": "Ana Ejemplo",
  "email": "ana@example.test",
  "password": "<contraseña>"
}
```

El registro crea un usuario activo con rol `user`. El login devuelve `access_token`, `token_type` y `user`.

### Consulta RAG

```json
POST /query/
{
  "query": "¿Cuántos días de vacaciones corresponden?",
  "limit": 5
}
```

La respuesta tiene esta forma conceptual:

```json
{
  "answer": "...",
  "sources": [
    {"filename": "politica.pdf", "page_number": 3}
  ],
  "has_sufficient_context": true
}
```

En fuentes DOCX o Markdown, `page_number` es `null`; la interfaz muestra únicamente el nombre del documento. `/search/` devuelve los resultados recuperados y sus scores, mientras que `/query/` ejecuta también la detección de contexto y la generación con el LLM.

### Subida de documentos

La subida es `multipart/form-data`, no JSON. Un formulario válido incluye:

```text
file=<archivo>
visibility=departments
allowed_departments=rrhh
allowed_departments=tecnico
```

Para un documento personal se usa `visibility=personal`, `owner_user_id=<id>` y cero o más departamentos autorizados. Para uno general se usa `visibility=all`.

## Respuestas HTTP y errores esperados

| Código | Casos típicos |
|---|---|
| `201` | Registro, creación de usuario, conversación o mensaje |
| `204` | Borrado correcto de documento o usuario |
| `401` | Falta token válido o credenciales incorrectas |
| `403` | Usuario autenticado sin privilegio de administrador |
| `404` | Recurso inexistente o conversación ajena/no visible |
| `409` | Email duplicado o intento de retirar el último admin |
| `415` | Extensión de archivo no admitida |
| `422` | Cuerpo, formulario o metadata de acceso no válida |
| `503` | Error al llamar al servicio LLM |

## Propiedad y límites de conversaciones

Las rutas de conversación reciben el ID de la conversación, pero cada consulta comprueba que pertenezca a la cuenta autenticada. La API no permite leer, renombrar o eliminar conversaciones de otra persona. Los mensajes aceptan contenido de hasta 5.000 caracteres y un límite de recuperación de 1 a 20 resultados.

## Notas de administración

- Un administrador puede listar usuarios, crear cuentas, modificar rol/estado/departamentos y borrar cuentas.
- El backend bloquea autoeliminación y autodesactivación, además de dejar siempre al menos un administrador activo.
- La subida y borrado documental están protegidos en el backend; ocultar controles en la interfaz no sustituye estas comprobaciones.
- El borrado busca por filename exacto en Qdrant y elimina todos los chunks con ese valor. No es un endpoint de listado ni distingue documentos homónimos almacenados con el mismo filename.
