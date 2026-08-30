# Resultados de evaluación

## Objetivo

Este documento recoge los resultados de la evaluación inicial del sistema de recuperación y generación de DocuWise.

La evaluación se ha realizado utilizando un conjunto de casos de prueba definidos manualmente a partir del contenido de un documento corporativo relacionado con vacaciones, jornada laboral y permisos.

El objetivo de la evaluación es comprobar:

* La capacidad del sistema para recuperar información relevante.
* La capacidad para recuperar las páginas esperadas.
* La presencia de al menos una fuente relevante entre los resultados.
* La capacidad para detectar si existe contexto suficiente para responder.
* El comportamiento del sistema ante preguntas fuera del dominio de los documentos.

---

# Configuración de la evaluación

La evaluación se ha realizado utilizando los siguientes parámetros:

* Número de resultados recuperados: `Top K = 5`
* Modelo de embeddings: modelo de `sentence-transformers` con embeddings de 384 dimensiones.
* Base de datos vectorial: Qdrant.
* Métrica de similitud: similitud coseno.
* Umbral mínimo de contexto suficiente: `0.4`.
* Modelo de lenguaje: `gpt-5.6-luna`.

Cada pregunta se procesa a través del pipeline RAG completo:

```text
Pregunta
    ↓
Embedding de la pregunta
    ↓
Búsqueda vectorial en Qdrant
    ↓
Recuperación de los 5 resultados más relevantes
    ↓
Evaluación de contexto suficiente
    ↓
Generación de respuesta o rechazo
```

---

# Casos evaluados

Se evaluaron preguntas relacionadas con diferentes áreas del documento:

* Gestión general de vacaciones.
* Solicitud de vacaciones.
* Aprobación de vacaciones.
* Vacaciones e incapacidad temporal.
* Duración de la jornada laboral.
* Tipos de jornada laboral.
* Tipos de permisos.
* Solicitud de permisos.
* Preguntas fuera del dominio del documento.

También se incluyeron preguntas que no podían responderse utilizando la documentación disponible, con el objetivo de comprobar el funcionamiento del mecanismo de detección de contexto insuficiente.

---

# Métricas utilizadas

## Precision@5

Mide la proporción de resultados recuperados entre los cinco primeros que pertenecen al conjunto de páginas consideradas relevantes.

Resultado:

```text
Precision@5 media: 0.525
```

Esto indica que, de media, aproximadamente el 52,5 % de los resultados recuperados entre los cinco primeros pertenecen a páginas marcadas como relevantes durante la evaluación.

---

## Recall@5

Mide qué proporción de las páginas relevantes esperadas ha sido recuperada dentro de los cinco primeros resultados.

Resultado:

```text
Recall@5 medio: 0.9375
```

El sistema ha recuperado aproximadamente el 93,75 % de las páginas relevantes esperadas.

Este resultado indica una alta capacidad para encontrar la información necesaria dentro de los primeros resultados de la búsqueda vectorial.

---

## Hit@5

Indica si existe al menos un resultado relevante dentro de los cinco primeros resultados recuperados.

Resultado:

```text
Hit@5 medio: 1.0
```

Esto significa que el sistema ha encontrado al menos una fuente relevante dentro de los cinco primeros resultados en el 100 % de las preguntas válidas evaluadas.

---

## Context Detection Accuracy

Evalúa si el sistema ha detectado correctamente cuándo existe contexto suficiente para responder.

Resultado:

```text
Context Detection Accuracy: 1.0
```

El sistema ha clasificado correctamente todas las preguntas evaluadas respecto a la existencia o ausencia de contexto suficiente.

Esto incluye tanto preguntas respondibles mediante los documentos como preguntas fuera del dominio.

---

# Resultados finales

```text
Precision@5 media: 0.525
Recall@5 medio: 0.9375
Hit@5 medio: 1.0
Context Detection Accuracy: 1.0
```

---

# Interpretación

Los resultados muestran que el sistema presenta un buen rendimiento en la recuperación de información relevante.

La métrica más destacable es el `Recall@5` de `0.9375`, lo que indica que la gran mayoría de las páginas consideradas relevantes han sido recuperadas entre los cinco primeros resultados.

El `Hit@5` de `1.0` demuestra que, en todas las preguntas válidas evaluadas, el sistema ha recuperado al menos una fuente relevante.

Por su parte, el `Context Detection Accuracy` de `1.0` indica que el mecanismo de detección de contexto suficiente ha funcionado correctamente en todos los casos de prueba, incluyendo las preguntas fuera del dominio de los documentos.

La `Precision@5` es inferior al resto de métricas, con un valor de `0.525`. Esto no implica necesariamente un mal funcionamiento del sistema, ya que la evaluación se realiza comparando resultados recuperados con páginas esperadas. Un mismo documento puede generar múltiples chunks pertenecientes a la misma página, y algunos resultados pueden ser semánticamente relacionados aunque no pertenezcan exactamente a las páginas seleccionadas manualmente como relevantes.

---

# Conclusión

La evaluación inicial demuestra que DocuWise es capaz de:

* Recuperar información relevante mediante búsqueda semántica.
* Encontrar fuentes relevantes para las preguntas válidas evaluadas.
* Recuperar la mayoría de las páginas esperadas.
* Detectar correctamente cuándo existe contexto suficiente.
* Evitar generar respuestas cuando la pregunta no puede responderse con la información disponible.
* Responder utilizando un pipeline RAG basado en recuperación documental.

Los resultados obtenidos validan el funcionamiento de la primera versión del sistema y proporcionan una base inicial para futuras mejoras en recuperación, evaluación y generación de respuestas.
