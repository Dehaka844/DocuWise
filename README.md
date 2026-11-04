# DocuWise 2.0

DocuWise es una aplicación web privada para consultar documentación empresarial mediante **Retrieval-Augmented Generation (RAG)**. Permite gestionar usuarios, departamentos y permisos de acceso a documentos; recuperar fragmentos autorizados desde Qdrant; y generar respuestas con un modelo de lenguaje.

Esta versión incluye autenticación, conversaciones persistidas, administración de usuarios y documentos, control de acceso por departamento y propietario, reformulación de preguntas con historial y prompts orientados por ámbito.

## Funcionalidades

- Ingesta de PDF, DOCX y Markdown; el parser DOCX conserva párrafos y tablas.
- Embeddings multilingües de 384 dimensiones y búsqueda vectorial en Qdrant.
- Acceso a documentos generales, departamentales y personales.
- Respuestas basadas en fragmentos que superan el umbral configurado, con fuentes.
- Reformulación de preguntas cuando hay historial de conversación.
- Registro y login con JWT; PostgreSQL almacena usuarios, conversaciones, mensajes y fuentes.
- Panel de administración para gestionar usuarios y documentos.
- Interfaz web servida por FastAPI.

## Arquitectura

```text
Documento --admin--> Parser PDF/DOCX/MD --> Chunking --> Embeddings --> Qdrant
                                                                  ▲
Usuario autenticado --> historial/reformulación --> búsqueda + filtro ACL
                                              --> fragmentos relevantes
                                              --> prompt común + ámbitos
                                              --> LLM --> respuesta + fuentes
                                                                  │
                                      PostgreSQL: usuarios, conversaciones,
                                                  mensajes y fuentes
```

| Componente | Función |
|---|---|
| FastAPI | API y servicio de archivos estáticos del frontend |
| PostgreSQL | Usuarios, roles, departamentos, conversaciones, mensajes y fuentes |
| Qdrant | Embeddings y payloads de fragmentos documentales |
| Sentence Transformers | Embeddings con `paraphrase-multilingual-MiniLM-L12-v2` |
| OpenAI | Reformulación contextual y generación de respuestas |
| LangGraph | Orquestación de los pasos del pipeline RAG |

## Control de acceso documental

Los roles son `user` y `admin`. Los departamentos (`rrhh`, `tecnico`, `marketing`) se asignan por separado del rol.

| Visibilidad | Quién puede consultar |
|---|---|
| `all` | Todas las cuentas activas; ámbito `general` |
| `departments` | Usuarios de al menos uno de los departamentos autorizados |
| `personal` | Propietario y usuarios de los departamentos autorizados |
| Administrador | Puede consultar todos los documentos |

Las consultas y búsquedas requieren autenticación. La subida y eliminación de documentos y los endpoints `/admin/users` requieren un administrador. La interfaz oculta opciones según el rol, pero los permisos también se comprueban en el backend.

## Requisitos

- Python 3.12 o compatible con las dependencias del proyecto.
- Docker y Docker Compose.
- Una clave de API de OpenAI.
- Node.js/npm solo si vas a recompilar el frontend.

## Instalación local

1. Clona el repositorio y entra en la carpeta:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd docuwise
   ```

2. Inicia Qdrant y PostgreSQL:

   ```bash
   docker compose up -d
   ```

3. Crea el entorno e instala dependencias:

   ```bash
   python -m venv .venv
   ```

   En Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   En Linux/macOS:

   ```bash
   source .venv/bin/activate
   ```

   Después:

   ```bash
   pip install -r requirements.txt
   ```

4. Copia `.env.example` como `.env` y configura `OPENAI_API_KEY` y un `JWT_SECRET_KEY` propio. Para el Compose local incluido, `POSTGRES_PASSWORD` debe coincidir con el valor de PostgreSQL en `docker-compose.yml` (`docuwise_password` por defecto). Cambia las credenciales de ejemplo antes de usarlo fuera de un entorno local.

5. Aplica las migraciones de base de datos:

   ```bash
   alembic upgrade head
   ```

6. Arranca la aplicación:

   ```bash
   uvicorn app.main:app --reload
   ```

La interfaz de login estará en <http://127.0.0.1:8000/frontend/index.html>. La API interactiva está en <http://127.0.0.1:8000/docs> y la comprobación de Qdrant en <http://127.0.0.1:8000/health>.

### Primer administrador

El registro público crea cuentas con rol `user`. Para iniciar una instalación local, registra una cuenta y promuévela una vez desde PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@empresa.example';
```

Después, vuelve a iniciar sesión. En una instalación real, el alta inicial de administradores debe hacerse mediante un proceso de provisión seguro.

### Recompilar el frontend

El frontend compilado se sirve desde `frontend/`. Si modificas los archivos TypeScript o SCSS:

```bash
cd frontend
npm install
npm run build
```

Node.js no es necesario para ejecutar la aplicación una vez compilados los recursos.

## API principal

Todas las rutas y modelos están en `/docs`. Las operaciones de conversación, búsqueda y consulta requieren un token Bearer.

| Ruta | Acceso | Función |
|---|---|---|
| `POST /auth/register`, `POST /auth/login` | Público | Crear cuenta e iniciar sesión |
| `GET /auth/me` | Usuario | Consultar la cuenta actual |
| `POST /search/`, `POST /query/` | Usuario | Buscar fragmentos o generar una respuesta RAG |
| `POST /documents/`, `DELETE /documents/?filename=...` | Admin | Subir o eliminar un documento |
| `/conversations/` y `/conversations/{id}/messages` | Usuario propietario | Gestionar conversaciones y mensajes |
| `/admin/users/` y `/admin/users/{id}` | Admin | Crear, listar, actualizar acceso o borrar usuarios |
| `GET /health` | Público | Consultar estado básico de Qdrant |

La eliminación de documentos borra los fragmentos cuyo `filename` coincide exactamente; usa nombres de archivo únicos para evitar ambigüedad.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Ingesta y parsers](docs/ingestion.md)
- [Recuperación y permisos](docs/retrieval.md)
- [Pipeline RAG](docs/rag_pipeline.md)
- [API](docs/api.md)
- [Evaluación](docs/evaluation.md)
- [Documentos ficticios de prueba](docs_example/)
- [Informes manuales de evaluación](informes/)

`docs_example/` contiene documentos ficticios. `informes/` contiene revisiones manuales de respuestas y fuentes; sus resultados no equivalen a una métrica automática reproducida.

## Estado de evaluación

La evaluación automática incluida conserva un conjunto histórico de preguntas sobre documentación de vacaciones de una versión anterior. Sus resultados no deben presentarse como métricas de DocuWise 2.0. La tanda manual actual se documenta en `informes/`; incluye casos correctos y fallos pendientes de recuperación y de mezcla entre documentos.
