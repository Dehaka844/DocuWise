# Evaluación

El repositorio contiene dos tipos de evidencia que conviene distinguir.

## Evaluador automático histórico

`evaluation/evaluate.py` ejecuta los casos definidos en `evaluation/test_cases.py` contra el pipeline y Qdrant. El conjunto actual evalúa preguntas sobre vacaciones, jornada y permisos de un documento de una versión anterior, con páginas esperadas. Las métricas implementadas son Precision@K, Recall@K, Hit@K y detección de contexto.

Los resultados almacenados en `evaluation/RESULTS.md` son una **línea base histórica de V1**. No se han vuelto a calcular sobre el corpus ficticio de V2 y no deben presentarse como evaluación actual. Para reproducir ese benchmark hace falta indexar la documentación original a la que hacen referencia sus páginas esperadas.

Ejecución desde la raíz:

```bash
python -m evaluation.evaluate
```

Requiere configuración, Qdrant con el corpus compatible, modelo de embeddings disponible y clave OpenAI. El evaluador invoca el pipeline completo y realiza llamadas al modelo.

## Informes manuales V2

`informes/` contiene revisiones de preguntas reales de prueba frente al contenido de documentos ficticios en `docs_example/`. El informe v2 revisa 18 respuestas, fuentes y permisos declarados. Es una evaluación manual: no equivale a una métrica automática ni sustituye un conjunto de referencia mantenido como código.

La revisión v2 mostró que la extracción de tablas DOCX mejoró varias respuestas, aunque siguen observándose omisiones, fuentes irrelevantes y confusión entre documentos. Esas limitaciones deben figurar al presentar resultados del TFG.

## Próximo paso para una evaluación reproducible

Convertir las preguntas del informe manual en casos estructurados con documento esperado, hechos requeridos, usuario/departamentos autorizados y criterios de evaluación de respuesta y fuente. Ejecutar la misma colección de preguntas tras cada cambio y registrar versión del corpus y configuración.

## Métricas del benchmark heredado

- **Precision@K:** proporción de resultados recuperados que pertenecen al conjunto esperado.
- **Recall@K:** proporción de páginas esperadas que aparecen en los resultados.
- **Hit@K:** 1 si aparece alguna página esperada y 0 si no aparece ninguna.
- **Context Detection Accuracy:** proporción de casos donde la decisión de contexto coincide con `expected_has_context`.

Estas métricas evalúan recuperación por página, no la corrección semántica de la respuesta. En V2, DOCX/Markdown no tienen página física indexada; un benchmark nuevo debería evaluar por chunk, hecho o sección, no comparar únicamente enteros de página.

## Revisión de respuestas y fuentes

La revisión manual de `informes/Informe_revision_lotes_RAG_v2.md` usa seis grupos temáticos y 18 preguntas. Para cada pregunta registra usuario/departamento declarado, respuesta resumida, fuentes visibles y juicio frente al contenido ficticio. Es útil para observar errores de completitud y mezcla de documentos, pero el resumen no conserva scores ni el texto exacto de todos los chunks enviados al LLM.

Al diseñar la siguiente evaluación se recomienda guardar por caso:

1. Pregunta y conversación previa relevante.
2. Usuario, departamentos, rol y documento permitido.
3. Fragmentos recuperados, scores y metadata de acceso (sin secretos).
4. Hechos que deben aparecer y hechos que no deben afirmarse.
5. Archivos/chunks que justifican la respuesta.
6. Resultado separado para recuperación, respuesta, fuente y autorización.

Las pruebas de autorización deberían incluir pares positivos y negativos: un usuario autorizado recupera el documento; otro usuario sin departamento ni propiedad no recupera su contenido ni su fuente. En este proyecto esas pruebas también se han ejecutado manualmente, aunque no estén reflejadas en el informe v2.

## Reproducibilidad y límites

Para comparar cambios hay que mantener o registrar el corpus, el estado de reindexación, el modelo de embeddings, el límite, el threshold, el prompt, el modelo LLM y la fecha/configuración del test. Cambiar parser o formato de chunk modifica los vectores y requiere reindexar los documentos de prueba. Las llamadas a OpenAI pueden variar entre ejecuciones; los resultados manuales deben identificarse como una muestra, no como una garantía estadística.
