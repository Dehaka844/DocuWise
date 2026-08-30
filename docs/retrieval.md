# Recuperación semántica

## Visión general

La recuperación semántica es la fase de DocuWise encargada de encontrar los fragmentos de documentos más relevantes para una pregunta realizada por el usuario.

Esta fase es fundamental dentro de la arquitectura RAG, ya que determina qué información documental será utilizada posteriormente como contexto para generar la respuesta.

El proceso general es:

```text
Pregunta del usuario

    ↓

Generación del embedding de la consulta

    ↓

Búsqueda vectorial en Qdrant

    ↓

Recuperación de los chunks más similares

    ↓

Resultados ordenados por similitud
```

El sistema utiliza búsqueda semántica en lugar de realizar únicamente coincidencias exactas de palabras.

Esto permite recuperar fragmentos relacionados conceptualmente con la pregunta aunque no utilicen exactamente las mismas palabras.

---

# RetrievalService

La lógica de recuperación se centraliza en:

```text
RetrievalService
```

Este servicio actúa como intermediario entre la consulta realizada por el usuario y el sistema de almacenamiento vectorial.

Sus principales responsabilidades son:

* Recibir la pregunta del usuario.
* Generar el embedding de la consulta.
* Solicitar la búsqueda vectorial a Qdrant.
* Recuperar los resultados más relevantes.
* Devolver los resultados al pipeline RAG.

La separación de esta responsabilidad permite mantener desacoplados:

```text
Pregunta
    ↓
RetrievalService
    ↓
QdrantService
```

De esta forma, el resto del sistema no necesita conocer los detalles internos de la búsqueda vectorial.

---

# Generación del embedding de la consulta

Para realizar una búsqueda semántica, la pregunta del usuario debe convertirse primero en un vector.

El proceso utiliza el mismo `EmbeddingService` empleado durante la ingestión de documentos.

El flujo es:

```text
Pregunta

    ↓

EmbeddingService

    ↓

Vector de 384 dimensiones
```

Por ejemplo, una pregunta como:

```text
¿Cómo se gestionan las vacaciones?
```

se transforma en un vector numérico de 384 dimensiones.

Este vector representa semánticamente el significado de la pregunta.

La utilización del mismo modelo de embeddings durante la ingestión y durante la recuperación es necesaria para que los vectores pertenezcan al mismo espacio semántico.

El proceso completo puede representarse como:

```text
Documento
    ↓
Chunk
    ↓
Embedding
    ↓
Qdrant


Pregunta
    ↓
Embedding
    ↓
Qdrant
```

Esto permite comparar directamente el vector de la pregunta con los vectores almacenados.

---

# Búsqueda vectorial

Una vez generado el embedding de la pregunta, `RetrievalService` solicita a `QdrantService` la búsqueda de los vectores más similares.

El flujo es:

```text
Embedding de la pregunta

        ↓

QdrantService

        ↓

Qdrant

        ↓

Vectores más similares

        ↓

Resultados recuperados
```

Qdrant compara el vector de la consulta con los vectores almacenados en la colección.

Los resultados se ordenan según su similitud con la consulta.

---

# QdrantService

La comunicación con la base de datos vectorial está encapsulada dentro de:

```text
QdrantService
```

Este servicio es responsable de interactuar directamente con Qdrant.

Entre sus responsabilidades se encuentran:

* Conectarse con la colección configurada.
* Almacenar embeddings.
* Realizar búsquedas vectoriales.
* Recuperar el payload asociado a cada vector.

De esta manera, `RetrievalService` no necesita gestionar directamente la comunicación con Qdrant.

La arquitectura queda separada de la siguiente forma:

```text
RetrievalService

        ↓

QdrantService

        ↓

Qdrant
```

Esta separación permite cambiar posteriormente la implementación de la base de datos vectorial sin tener que modificar la lógica de recuperación.

---

# Similitud coseno

La colección utilizada por DocuWise está configurada utilizando la métrica de similitud coseno.

La configuración actual es:

```text
Dimensiones: 384

Métrica: Cosine
```

La similitud coseno permite comparar la orientación de dos vectores dentro del espacio vectorial.

En el contexto de DocuWise, esto permite determinar qué embeddings representan contenidos semánticamente más cercanos a la pregunta.

Conceptualmente:

```text
Pregunta
    ↓
Vector de consulta

        ↕
  similitud coseno

        ↕

Vectores de documentos
```

Cuanto mayor sea la similitud entre la consulta y un chunk, mayor será su relevancia potencial para responder a la pregunta.

---

# Top-K

La recuperación utiliza un número máximo de resultados denominado `K`.

Actualmente DocuWise utiliza:

```text
Top K = 5
```

Esto significa que, por defecto, se recuperan los cinco fragmentos con mayor similitud respecto a la consulta.

El flujo es:

```text
Consulta

    ↓

Búsqueda en Qdrant

    ↓

Resultados ordenados

    ↓

Top 5
```

El valor puede modificarse mediante el parámetro `limit` utilizado durante la consulta.

Por ejemplo:

```python
graph.invoke(
    {
        "query": query,
        "limit": 5,
    }
)
```

El valor se transmite posteriormente al servicio de recuperación.

Esto permite controlar cuántos fragmentos se utilizan como candidatos para construir el contexto.

---

# Resultados de recuperación

Cada resultado recuperado contiene la información necesaria para continuar con el pipeline RAG.

Conceptualmente, un resultado contiene:

```text
Contenido
+
Score
+
Metadata
```

El contenido corresponde al texto del chunk.

El `score` representa el grado de similitud entre la consulta y el fragmento recuperado.

La metadata permite conocer el origen del contenido.

Entre los datos disponibles se encuentran:

```text
filename

source_type

page_count

page_number

chunk_index
```

Esta información permite mantener la trazabilidad del contenido recuperado.

---

# Ejemplo de resultado

Un resultado de recuperación puede representarse conceptualmente como:

```text
Resultado:

Score:
0.7420594

Página:
5

Contenido:
"retribuidas.
La duración de las vacaciones será la establecida
por la legislación laboral..."
```

La puntuación permite conocer la relevancia semántica del resultado.

Por ejemplo:

```text
Resultado 1
Score: 0.7420594
Página: 5

Resultado 2
Score: 0.6828543
Página: 19

Resultado 3
Score: 0.6306761
Página: 7

Resultado 4
Score: 0.6283475
Página: 18

Resultado 5
Score: 0.59850407
Página: 6
```

Los resultados aparecen ordenados de mayor a menor similitud.

---

# Score de similitud

El `score` obtenido durante la búsqueda es utilizado posteriormente por el pipeline RAG para determinar si existe suficiente contexto para responder.

Actualmente se utiliza el mejor resultado recuperado:

```text
best_score = results[0].score
```

Posteriormente se compara con un umbral:

```text
score_threshold = 0.4
```

La lógica es:

```text
Resultados recuperados

        ↓

Obtener mejor score

        ↓

¿score >= 0.4?

    ┌───────┴───────┐
    ↓               ↓
   Sí               No
    ↓               ↓
Contexto         Contexto
suficiente       insuficiente
```

Esta comprobación forma parte del pipeline RAG y se documentará con mayor detalle en `rag_pipeline.md`.

---

# Recuperación de preguntas relevantes

Una de las ventajas de la recuperación semántica es que no depende exclusivamente de coincidencias literales.

Por ejemplo, una pregunta como:

```text
¿Cómo se gestionan las vacaciones?
```

puede recuperar correctamente fragmentos que contienen expresiones como:

```text
La planificación de vacaciones...

Las solicitudes de vacaciones...

La aprobación de las vacaciones...

Las vacaciones deberán disfrutarse...
```

Aunque la pregunta y los fragmentos no utilicen exactamente las mismas palabras, sus embeddings pueden encontrarse próximos dentro del espacio semántico.

Esto permite realizar búsquedas basadas en significado.

---

# Recuperación de preguntas fuera del dominio

El sistema también utiliza la puntuación de similitud para detectar preguntas que no tienen relación suficiente con los documentos disponibles.

Por ejemplo:

```text
¿Cuál es la receta para hacer una tortilla de patatas?
```

puede producir resultados con puntuaciones muy inferiores a las obtenidas para preguntas relacionadas con los documentos.

Un ejemplo observado durante las pruebas fue:

```text
Score:
0.044032436
```

Aunque Qdrant devuelve resultados, la puntuación es demasiado baja para considerar que existe contexto suficiente.

En este caso:

```text
Score < 0.4
```

por lo que el pipeline no continúa hacia la generación con el modelo de lenguaje.

La respuesta se genera mediante el nodo de ausencia de contexto.

Esto evita utilizar información documental irrelevante para generar respuestas.

---

# Flujo completo de recuperación

El proceso completo puede resumirse de la siguiente manera:

```text
Pregunta del usuario

        ↓

RetrievalService

        ↓

EmbeddingService

        ↓

Embedding de 384 dimensiones

        ↓

QdrantService

        ↓

Búsqueda vectorial

        ↓

Similitud coseno

        ↓

Resultados ordenados

        ↓

Top-K

        ↓

Chunks recuperados
```

Posteriormente, estos resultados son enviados al pipeline RAG.

---

# Integración con el pipeline RAG

La recuperación no genera directamente la respuesta final.

Su responsabilidad termina cuando devuelve los resultados relevantes.

El flujo completo es:

```text
Pregunta
    ↓
RetrievalService
    ↓
Qdrant
    ↓
Resultados
    ↓
Comprobación de contexto
    ↓
┌──────────────────────┐
│                      │
│ Contexto suficiente? │
│                      │
└──────────┬───────────┘
           │
      ┌────┴────┐
      ↓         ↓
     Sí         No
      ↓         ↓
   LLM       No Context
      ↓         ↓
      └────┬────┘
           ↓
       Respuesta
```

La recuperación constituye, por tanto, la primera parte del proceso de consulta RAG.

---

# Trazabilidad de los resultados

Los resultados recuperados conservan la metadata asociada a cada chunk.

Esto permite identificar posteriormente:

* El documento de origen.
* El tipo de documento.
* La página donde aparece la información.
* El índice del chunk.

Esta información se utiliza posteriormente para construir las fuentes que se muestran al usuario.

Por ejemplo:

```text
Fuente:

Política Interna de Vacaciones y Organización del Trabajo.pdf

Página: 5
```

La trazabilidad permite relacionar la respuesta generada con la información documental que ha sido recuperada.

---

# Responsabilidades de los componentes

La fase de recuperación se divide principalmente entre dos servicios.

## RetrievalService

Se encarga de coordinar la recuperación.

Sus responsabilidades son:

* Recibir la consulta.
* Solicitar el embedding.
* Solicitar la búsqueda vectorial.
* Devolver los resultados.

## QdrantService

Se encarga de la interacción con Qdrant.

Sus responsabilidades son:

* Gestionar la conexión con Qdrant.
* Ejecutar búsquedas vectoriales.
* Recuperar vectores y payloads.

La separación es:

```text
RetrievalService
      │
      │ coordina
      ▼
QdrantService
      │
      │ consulta
      ▼
Qdrant
```

---

# Decisiones técnicas

La implementación actual utiliza varias decisiones técnicas relevantes.

## Embeddings

Los embeddings utilizados tienen:

```text
384 dimensiones
```

El mismo modelo se utiliza tanto para indexar los documentos como para representar las consultas.

## Métrica

La colección utiliza:

```text
Cosine
```

como métrica de similitud.

## Número de resultados

El valor utilizado actualmente es:

```text
Top-K = 5
```

## Umbral de contexto

El pipeline considera suficiente el contexto cuando:

```text
best_score >= 0.4
```

Estas decisiones permiten mantener un pipeline sencillo y adecuado para la primera versión del proyecto.

---

# Evaluación de la recuperación

La recuperación semántica se ha evaluado mediante un conjunto de preguntas reales relacionadas con el documento utilizado durante las pruebas.

Las métricas utilizadas son:

```text
Precision@5

Recall@5

Hit@5
```

Los resultados obtenidos actualmente son:

```text
Precision@5 media: 0.525

Recall@5 medio: 0.9375

Hit@5 medio: 1.0
```

Estos resultados muestran que el sistema consigue recuperar al menos un fragmento relevante en todos los casos evaluados.

El `Recall@5` elevado indica que la mayoría de las páginas consideradas relevantes aparecen dentro de los cinco resultados recuperados.

La evaluación completa del sistema se documenta en:

```text
docs/evaluation.md
```

---

# Limitaciones actuales

La recuperación implementada actualmente es intencionadamente sencilla.

Entre sus principales limitaciones se encuentran:

* La búsqueda utiliza una única consulta vectorial.
* El número de resultados está limitado mediante Top-K.
* La detección de contexto utiliza únicamente el mejor `score`.
* No existe actualmente un reranker posterior a la búsqueda vectorial.
* No se realizan búsquedas híbridas combinando búsqueda semántica y búsqueda léxica.
* No se aplican filtros por colección, departamento u otros atributos.

Estas funcionalidades pueden incorporarse posteriormente como mejoras del sistema.

---

# Resumen

La recuperación semántica de DocuWise transforma la pregunta del usuario en un embedding y utiliza dicho vector para localizar los fragmentos más similares almacenados en Qdrant.

El proceso es:

```text
Pregunta

    ↓

Embedding de 384 dimensiones

    ↓

Búsqueda por similitud coseno

    ↓

Qdrant

    ↓

Top-K resultados

    ↓

Chunks relevantes

    ↓

Comprobación de contexto
```

La recuperación mantiene además la metadata necesaria para identificar el origen de cada fragmento.

De esta forma, DocuWise puede utilizar los resultados recuperados como contexto para generar respuestas fundamentadas en los documentos proporcionados por el usuario.

La siguiente fase del sistema es el pipeline RAG, donde los resultados recuperados son evaluados y, cuando existe contexto suficiente, enviados al modelo de lenguaje para generar la respuesta final.

Esta fase se documenta en:

```text
docs/rag_pipeline.md
```
