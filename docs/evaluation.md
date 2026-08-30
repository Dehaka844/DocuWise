# Evaluación

## 1. Introducción

DocuWise incorpora un sistema de evaluación destinado a comprobar el funcionamiento del pipeline RAG y medir objetivamente la calidad de la recuperación de información.

La evaluación se centra principalmente en tres aspectos:

- La capacidad del sistema para recuperar las páginas relevantes.
- La capacidad para recuperar la información relevante dentro de los primeros resultados.
- La capacidad del sistema para determinar si existe suficiente contexto para responder a una pregunta.

Además, se incluyen preguntas que están fuera del dominio de los documentos para comprobar que el sistema no genere respuestas cuando no existe información suficientemente relevante.

La evaluación se encuentra dentro de la carpeta:

```text
evaluation/
````

Su estructura actual es:

```text
evaluation/
├── evaluate.py
├── metrics.py
├── test_cases.py
└── RESULTS.md
```

---

## 2. Objetivos de la evaluación

El objetivo principal es comprobar que DocuWise puede realizar correctamente las diferentes etapas del sistema RAG.

En concreto, se evalúa que:

1. Una pregunta relacionada con los documentos encuentre información relevante.
2. Los resultados relevantes aparezcan entre los primeros resultados recuperados.
3. El sistema sea capaz de recuperar la mayoría de las páginas relevantes.
4. Al menos un resultado relevante aparezca entre los resultados recuperados.
5. El sistema detecte cuándo existe suficiente contexto para responder.
6. El sistema rechace preguntas que no pertenecen al contenido de los documentos.
7. Las respuestas generadas por el LLM se basen en el contexto recuperado.

La evaluación está orientada principalmente a la recuperación y al comportamiento del pipeline, no a realizar una evaluación lingüística exhaustiva de la calidad de las respuestas generadas.

---

# 3. Casos de prueba

Los casos de prueba se encuentran definidos en:

```text
evaluation/test_cases.py
```

Cada caso contiene la información necesaria para determinar qué debería recuperar el sistema.

Conceptualmente, cada caso incluye:

```python
{
    "name": "...",
    "query": "...",
    "expected_pages": [...],
    "expected_has_context": True
}
```

Los campos tienen las siguientes funciones:

### `name`

Nombre descriptivo del caso de prueba.

Permite identificar fácilmente el escenario durante la ejecución de la evaluación.

### `query`

Pregunta que se envía al sistema RAG.

### `expected_pages`

Lista de páginas que se consideran relevantes para responder correctamente a la pregunta.

Estas páginas se utilizan como referencia para calcular las métricas de recuperación.

### `expected_has_context`

Indica si se espera que exista suficiente información en los documentos para responder a la pregunta.

Se utiliza para evaluar la detección de contexto.

---

# 4. Tipos de casos evaluados

Los casos de prueba utilizados cubren diferentes partes del contenido del documento.

## 4.1. Preguntas sobre vacaciones

Se incluyen preguntas relacionadas con:

* Gestión general de vacaciones.
* Solicitud de vacaciones.
* Aprobación de vacaciones.
* Vacaciones durante una incapacidad temporal.

Estos casos permiten comprobar la recuperación de diferentes secciones relacionadas entre sí.

---

## 4.2. Preguntas sobre jornada laboral

También se incluyen preguntas relacionadas con:

* Duración de la jornada laboral.
* Tipos de jornada laboral.

Estos casos permiten comprobar que el sistema puede recuperar información de otras partes del documento y no únicamente de la sección de vacaciones.

---

## 4.3. Preguntas sobre permisos

Se utilizan casos relacionados con:

* Tipos de permisos.
* Solicitud de permisos.

Estos casos permiten comprobar la recuperación de información de otra sección temática del documento.

---

## 4.4. Preguntas fuera del dominio

La evaluación también contiene preguntas que no están relacionadas con el contenido disponible.

Por ejemplo:

```text
¿Cuál es la receta para hacer una tortilla de patatas?
```

y:

```text
¿Cómo se instala PostgreSQL en un servidor?
```

En estos casos se espera:

```python
"expected_has_context": False
```

El objetivo es comprobar que DocuWise no intente responder utilizando conocimiento externo cuando los documentos no contienen información relevante.

---

# 5. Ejecución de la evaluación

La evaluación se ejecuta desde la raíz del proyecto mediante:

```bash
python -m evaluation.evaluate
```

Es importante ejecutarla como módulo para que Python pueda resolver correctamente los imports del proyecto, especialmente los imports del paquete `app`.

Antes de ejecutar la evaluación es necesario disponer de:

* Las dependencias instaladas.
* Las variables de entorno configuradas.
* Qdrant disponible.
* La colección de Qdrant con los documentos previamente indexados.
* Acceso al modelo de embeddings.
* Acceso al modelo de lenguaje utilizado por DocuWise.

---

# 6. Funcionamiento de `evaluate.py`

El archivo:

```text
evaluation/evaluate.py
```

es el encargado de ejecutar todos los casos de prueba y calcular las métricas.

El flujo general es:

```text
Cargar configuración
       ↓
Crear EmbeddingService
       ↓
Crear QdrantService
       ↓
Crear RetrievalService
       ↓
Crear LLMService
       ↓
Crear QueryGraph
       ↓
Ejecutar cada caso de prueba
       ↓
Obtener resultados de recuperación
       ↓
Calcular métricas
       ↓
Mostrar respuesta generada
       ↓
Calcular resultados medios
```

---

# 7. Inicialización de los servicios

Durante el inicio de la evaluación se crean las mismas piezas principales que utiliza el sistema RAG:

```python
embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

llm_service = LLMService()
```

Posteriormente se crea el grafo de consulta:

```python
query_graph = QueryGraph(
    retrieval_service=retrieval_service,
    llm_service=llm_service,
)

graph = query_graph.build()
```

De esta forma, la evaluación utiliza el mismo pipeline RAG que la aplicación.

Esto permite evaluar el comportamiento real del sistema en lugar de crear una implementación independiente exclusivamente para los tests.

---

# 8. Número de resultados evaluados

La evaluación utiliza:

```python
TOP_K = 5
```

Esto significa que para cada pregunta se solicitan los cinco primeros resultados de recuperación.

Estos cinco resultados se utilizan para calcular las métricas relacionadas con la recuperación.

---

# 9. Obtención de resultados

Para cada caso de prueba se ejecuta el grafo:

```python
graph_result = graph.invoke(
    {
        "query": test_case["query"],
        "limit": TOP_K,
    }
)
```

El resultado contiene, entre otra información:

* Los resultados recuperados.
* Si existe suficiente contexto.
* La respuesta generada.
* Las fuentes utilizadas.

Las páginas recuperadas se extraen de los metadatos:

```python
retrieved_pages = [
    retrieval_result.metadata["page_number"]
    for retrieval_result in graph_result["results"]
]
```

De esta manera se puede comparar directamente:

```text
Páginas esperadas
        vs.
Páginas recuperadas
```

---

# 10. Métricas

Las métricas utilizadas se encuentran en:

```text
evaluation/metrics.py
```

Actualmente se calculan cuatro métricas principales:

* Precision@K.
* Recall@K.
* Hit@K.
* Context Detection Accuracy.

---

# 11. Precision@K

La métrica Precision@K mide qué proporción de los resultados recuperados pertenece al conjunto de páginas consideradas relevantes.

Para DocuWise:

```text
Precision@5 =
resultados relevantes dentro de los 5 primeros
------------------------------------------------
número de resultados recuperados
```

Por ejemplo, si se recuperan:

```text
[5, 19, 7, 18, 6]
```

y las páginas relevantes son:

```text
[5, 6, 7, 19]
```

hay cuatro resultados relevantes dentro de los cinco recuperados.

Por tanto:

```text
Precision@5 = 4 / 5 = 0.8
```

Esta métrica permite comprobar si los primeros resultados contienen información relevante o si existe demasiado contenido irrelevante entre ellos.

---

# 12. Recall@K

Recall@K mide qué proporción de las páginas relevantes conocidas ha conseguido recuperar el sistema.

La fórmula utilizada es:

```text
Recall@K =
páginas relevantes recuperadas
------------------------------
páginas relevantes esperadas
```

Por ejemplo, si las páginas esperadas son:

```text
[5, 6, 7, 19]
```

y el sistema recupera:

```text
[5, 19, 7, 18, 6]
```

se han recuperado las cuatro páginas relevantes.

Por tanto:

```text
Recall@5 = 4 / 4 = 1.0
```

Esta métrica resulta especialmente útil para comprobar si el sistema está perdiendo información relevante.

---

# 13. Hit@K

Hit@K indica si al menos una página relevante aparece entre los resultados recuperados.

El resultado puede ser:

```text
1.0
```

si existe al menos una coincidencia, o:

```text
0.0
```

si no existe ninguna.

Por ejemplo:

```text
Páginas esperadas:
[5, 6, 7, 19]

Páginas recuperadas:
[12, 8, 5, 3, 20]
```

Como la página `5` es relevante:

```text
Hit@5 = 1.0
```

Esta métrica permite determinar rápidamente si el sistema ha encontrado al menos una fuente relevante.

---

# 14. Context Detection Accuracy

Esta métrica evalúa si el sistema ha tomado correctamente la decisión de considerar que existe o no suficiente contexto.

Se compara:

```text
expected_has_context
```

con:

```text
actual_has_context
```

La métrica devuelve:

```text
1.0
```

cuando ambas decisiones coinciden y:

```text
0.0
```

cuando son diferentes.

Por ejemplo:

```text
Contexto esperado: True
Contexto obtenido: True

Accuracy = 1.0
```

O:

```text
Contexto esperado: False
Contexto obtenido: True

Accuracy = 0.0
```

Esta métrica es especialmente importante para las preguntas fuera del dominio.

---

# 15. Relación entre las métricas

Las cuatro métricas proporcionan información diferente.

| Métrica                    | Qué mide                                                      |
| -------------------------- | ------------------------------------------------------------- |
| Precision@5                | Cuántos de los resultados recuperados son relevantes          |
| Recall@5                   | Cuánta información relevante se ha recuperado                 |
| Hit@5                      | Si existe al menos un resultado relevante                     |
| Context Detection Accuracy | Si el sistema detecta correctamente la existencia de contexto |

No deben interpretarse como métricas equivalentes.

Por ejemplo, un sistema puede obtener un Hit@5 perfecto porque siempre encuentra al menos un resultado relevante, pero tener una Precision@5 más baja porque también recupera documentos irrelevantes.

---

# 16. Resultados obtenidos

La evaluación actual del proyecto produjo los siguientes resultados:

```text
Precision@5 media: 0.525
Recall@5 medio: 0.9375
Hit@5 medio: 1.0
Context Detection Accuracy: 1.0
```

Estos resultados se encuentran registrados en:

```text
evaluation/RESULTS.md
```

---

# 17. Interpretación de los resultados actuales

## Precision@5

```text
0.525
```

La Precision@5 media indica que, de media, aproximadamente el 52,5 % de los resultados recuperados entre los cinco primeros corresponden a páginas consideradas relevantes en los casos de evaluación.

Esta métrica es mejorable, especialmente en preguntas muy concretas donde Qdrant puede recuperar contenido relacionado pero no estrictamente necesario para responder.

---

## Recall@5

```text
0.9375
```

El Recall@5 obtenido es alto.

Esto indica que el sistema está recuperando la mayor parte de las páginas relevantes definidas en los casos de evaluación.

Para un sistema RAG esto es especialmente positivo porque una buena recuperación de contexto aumenta las posibilidades de que el LLM disponga de la información necesaria para generar una respuesta correcta.

---

## Hit@5

```text
1.0
```

El Hit@5 es perfecto en los casos evaluados.

Esto significa que siempre se encontró al menos una página relevante entre los cinco primeros resultados de recuperación.

---

## Context Detection Accuracy

```text
1.0
```

El sistema obtuvo una precisión perfecta en la detección de contexto para los casos evaluados.

Esto significa que distinguió correctamente entre:

```text
Preguntas con contexto suficiente
```

y:

```text
Preguntas sin contexto suficiente
```

incluyendo las preguntas fuera del dominio utilizadas durante la evaluación.

---

# 18. Ejemplo de resultado de evaluación

Durante la ejecución se muestra información similar a:

```text
======================================================================
Evaluando: gestión general de vacaciones
Pregunta: ¿Cómo se gestionan las vacaciones?
----------------------------------------------------------------------
Contexto esperado: True
Contexto obtenido: True
Context Detection: 1.0
Páginas esperadas: [5, 6, 7, 19]
Páginas recuperadas: [5, 19, 7, 18, 6]
Precision@5: 0.8
```

Esto permite inspeccionar individualmente el comportamiento del sistema para cada pregunta.

Además, se muestra la respuesta generada por el LLM para comprobar manualmente que la información recuperada se utiliza correctamente.

---

# 19. Evaluación de preguntas fuera del dominio

Los casos fuera del dominio son especialmente importantes para comprobar el comportamiento del sistema cuando no existe información suficiente.

Por ejemplo:

```text
Pregunta:
¿Cuál es la receta para hacer una tortilla de patatas?

Contexto esperado:
False
```

Aunque Qdrant puede devolver resultados con una similitud baja debido a que siempre está realizando una búsqueda semántica, el `QueryGraph` utiliza un umbral para determinar si el contexto es suficientemente relevante.

Actualmente:

```python
score_threshold = 0.4
```

Por tanto, si la mejor coincidencia no alcanza ese umbral, el grafo no ejecuta la generación mediante el LLM y devuelve directamente un mensaje indicando que no existe información suficientemente relevante.

Esto permite evitar que el modelo utilice conocimiento externo para contestar preguntas que no están cubiertas por los documentos.

---

# 20. Limitaciones de la evaluación actual

La evaluación actual está centrada principalmente en la recuperación.

No se realiza todavía una evaluación automática avanzada de la calidad de las respuestas generadas por el LLM.

Por ejemplo, actualmente no se calculan automáticamente métricas específicas para:

* Fidelidad de la respuesta respecto al contexto.
* Completitud de la respuesta.
* Corrección semántica.
* Calidad lingüística.
* Detección automática de alucinaciones.

La calidad de las respuestas generadas se comprueba actualmente mediante inspección de los resultados obtenidos.

---

# 21. Posibles mejoras futuras

La evaluación puede ampliarse en futuras versiones del proyecto.

Algunas posibles mejoras son:

### Evaluación de respuestas

Crear respuestas esperadas para cada pregunta y comparar automáticamente la respuesta generada con ellas.

### Evaluación de faithfulness

Comprobar si las afirmaciones de la respuesta están respaldadas por el contexto recuperado.

### Evaluación de relevancia

Determinar si la respuesta responde realmente a la pregunta planteada.

### Mayor número de casos

Ampliar el conjunto de preguntas para cubrir más secciones y escenarios.

### Casos adversariales

Incluir preguntas ambiguas, preguntas mal formuladas y diferentes formas de expresar la misma consulta.

### Evaluación de seguridad

Añadir pruebas específicas para prompt injection y preguntas que intenten modificar el comportamiento del asistente.

### Comparación de configuraciones

Permitir comparar diferentes:

* Modelos de embedding.
* Modelos LLM.
* Valores de `TOP_K`.
* Umbrales de similitud.
* Estrategias de chunking.

Esto permitiría medir objetivamente qué configuración ofrece mejores resultados.

---

# 22. Reproducibilidad

Para que los resultados de la evaluación sean comparables, es importante mantener constantes las principales condiciones de la prueba.

Especialmente:

* Mismo conjunto de documentos.
* Misma colección de Qdrant.
* Mismo modelo de embeddings.
* Mismo conjunto de casos de prueba.
* Mismo valor de `TOP_K`.
* Misma configuración del sistema RAG.

Si alguno de estos elementos cambia, los resultados pueden variar y deben considerarse una nueva ejecución de evaluación.

---

# 23. Flujo completo de evaluación

El proceso completo puede resumirse de la siguiente manera:

```text
                 TEST_CASES
                     │
                     ▼
              evaluation.py
                     │
                     ▼
                QueryGraph
                     │
                     ▼
                Retrieval
                     │
                     ▼
                  Qdrant
                     │
                     ▼
             Resultados Top-K
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Precision    Recall      Hit
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
          Detección de contexto
                     │
                     ▼
              Generación LLM
                     │
                     ▼
              Respuesta final
                     │
                     ▼
             Resultados globales
```

---

# 24. Conclusión

El sistema de evaluación proporciona una forma reproducible de comprobar el comportamiento del pipeline RAG de DocuWise.

La evaluación actual demuestra que el sistema:

* Recupera la mayoría de las páginas relevantes.
* Encuentra al menos una fuente relevante en todos los casos evaluados.
* Detecta correctamente cuándo existe suficiente contexto.
* Evita generar respuestas para las preguntas fuera del dominio utilizadas en las pruebas.

Los resultados actuales son:

```text
Precision@5 media:          0.525
Recall@5 medio:             0.9375
Hit@5 medio:                1.0
Context Detection Accuracy: 1.0
```

La evaluación queda preparada para ampliarse posteriormente con métricas de calidad de respuesta, pruebas de seguridad y comparaciones entre diferentes configuraciones del sistema RAG.

```
```
