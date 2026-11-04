# Informe de revisión de pruebas RAG

**Proyecto:** DocuWise, versión 2  
**Fecha de revisión:** 4 de noviembre de 2026  
**Alcance:** seis lotes de respuestas, 18 preguntas en total. Se resumen las respuestas mostradas por el RAG y se comparan con los documentos de `docs_example`.

## Usuarios y alcance de acceso declarado

| Lote | Usuario | Departamento / condición comunicada | Documento consultado |
|---|---|---|---|
| 1 | `prueba` | Sin departamentos asignados; es propietario del CV cargado. | Reglas generales de Lumenia Labs |
| 2 | `prueba` | Sin departamentos asignados; es propietario del CV cargado. | CV de Claudia Serrano Vidal |
| 3 | `rrhh` | Pertenece al departamento de Recursos Humanos. | Información restringida de Recursos Humanos |
| 4 | `tec` | Pertenece al departamento técnico. | Diseño técnico del proyecto Atlas |
| 5 | `tec` | Pertenece al departamento técnico; el documento es un trabajo conjunto de Ingeniería y Marketing. | Proyecto Faro para el lanzamiento de Nido |
| 6 | `mk` | Pertenece al departamento de Marketing. | Propuesta de marketing y ventas de Círculo Verde |

> Nota: el primer usuario (`prueba`) aparece en dos lotes separados: uno sobre reglas generales y otro sobre su propio CV.

## 1. Reglas generales — usuario `prueba`

**Acceso declarado:** sin departamento; propietario del CV. Las reglas generales se consultaron como documentación general de empresa.

### Pregunta 1

**Pregunta:** ¿Cuál es el horario estándar y qué franja de flexibilidad de entrada permite la empresa?

**Respuesta del RAG:** dijo que el horario estándar no se especificaba; indicó entrada flexible entre 08:00 y 10:00 y disponibilidad común entre 10:00 y 14:00.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Parcialmente correcta, con un dato principal omitido y una afirmación errónea.** El documento sí fija el horario estándar: 09:00–18:00, con pausa de comida de 14:00–15:00. La franja flexible y la disponibilidad común sí se respondieron bien.

### Pregunta 2

**Pregunta:** ¿Cuántos días laborables de vacaciones corresponden al año y con cuánta antelación deben solicitarse?

**Respuesta del RAG:** 25 días laborables por año natural; solicitud con al menos 10 días laborables de antelación mediante NexoPeople.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.**

### Pregunta 3

**Pregunta:** ¿Qué límites de gasto se aplican al alojamiento y a la compra de equipos, y quién debe aprobar las excepciones?

**Respuesta del RAG:** alojamiento hasta 150 € por noche en España; las excepciones las aprueba Dirección antes de reservar. Compras de equipos: hasta 300 €, responsable; de 301 a 2.000 €, Dirección; más de 2.000 €, Dirección Financiera. Añadió que no se especifica otro procedimiento para excepciones de compra.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `CV_Claudia_Serrano_Vidal.docx — página 1`

**Evaluación:** **Mayormente correcta.** Los límites y aprobaciones coinciden con las reglas. La nota sobre excepciones de compra es una observación razonable sobre lo que el documento no detalla, pero no responde a un procedimiento definido.

## 2. CV — usuario `prueba`

**Acceso declarado:** sin departamento; propietario del CV cargado. La consulta del propio CV es coherente con ese contexto.

### Pregunta 1

**Pregunta:** ¿En qué empresas trabajó Claudia, en qué puestos y durante qué periodos?

**Respuesta del RAG:** Brújula Mobility, Senior Product Designer, abril de 2022–actualidad; AulaNube, Product Designer, enero de 2020–marzo de 2022; Estudio Norte, UX Designer, junio–diciembre de 2018.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** Las fechas y puestos coinciden. Las fuentes de reglas generales que acompañaban la respuesta eran irrelevantes.

### Pregunta 2

**Pregunta:** ¿Qué resultados obtuvo al rediseñar el alta de conductores en Brújula Mobility?

**Respuesta del RAG:** rediseñó el flujo de alta y redujo el abandono del 31 % al 19 % en dos trimestres.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Correcta.**

### Pregunta 3

**Pregunta:** ¿Qué estudios, idiomas y herramientas aparecen en su perfil?

**Respuesta del RAG:** mencionó formación complementaria en accesibilidad digital (2024), investigación cualitativa aplicada (2021) y facilitación de talleres (2020); dijo que no se especifican idiomas ni herramientas concretas.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Incorrecta e incompleta.** Omitió el Máster en Diseño de Interacción (Universitat Politècnica de València, 2017–2018) y el Grado en Comunicación Audiovisual (Universidad de Alicante, 2013–2017). También omitió español nativo, inglés C1, valenciano B2 y herramientas como Figma y FigJam, además de las competencias descritas en el CV.

## 3. Información de Recursos Humanos — usuario `rrhh`

**Acceso declarado:** departamento de Recursos Humanos. Las tres preguntas eran sobre el documento restringido de RR. HH.

### Pregunta 1

**Pregunta:** ¿Qué ajuste salarial recibirá Elena Vázquez en enero de 2027 y cuál será su nueva compensación anual?

**Respuesta del RAG:** ajuste del 4,5 % desde el 1 de enero de 2027; nueva compensación anual de 50.787 €.

**Fuentes mostradas en la captura:**

- `Acceso_restringido_Recursos_Humanos.pdf — página 1`
- `Acceso_restringido_Recursos_Humanos.pdf — página 2`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.**

### Pregunta 2

**Pregunta:** ¿Cómo se pagará la prima de retención de Tomás Rueda y qué condición debe cumplir para recibir cada tramo?

**Respuesta del RAG:** prima total de 3.000 €, en dos tramos de 1.500 € en marzo y septiembre de 2027; debe continuar en la empresa en la fecha correspondiente para recibir cada tramo.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Acceso_restringido_Recursos_Humanos.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Acceso_restringido_Recursos_Humanos.pdf — página 2`
- `CV_Claudia_Serrano_Vidal.docx — página 1`

**Evaluación:** **Correcta.** La respuesta incluía documentos adicionales no necesarios como fuentes.

### Pregunta 3

**Pregunta:** ¿Quiénes son las tres personas candidatas a Data Analyst y qué puntuación técnica obtuvo cada una?

**Respuesta del RAG:** Clara Beltrán, 4,6/5; Diego Pons, 4,2/5; Amina Ríos, 4,4/5.

**Fuentes mostradas en la captura:**

- `Acceso_restringido_Recursos_Humanos.pdf — página 2`
- `CV_Claudia_Serrano_Vidal.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** Aparecían también fuentes del CV y de reglas generales que no aportaban a esta consulta.

## 4. Diseño técnico de Atlas — usuario `tec`

**Acceso declarado:** departamento técnico. El usuario consultó documentación de Ingeniería de Plataforma.

### Pregunta 1

**Pregunta:** ¿Qué servicios y fuentes de eventos integra el piloto de Atlas y cuáles quedan fuera de su alcance?

**Respuesta del RAG:** incluye pedidos web de España; eventos de pago de PayRiver; preparación de almacén de StockPilot en Madrid y Valencia; y eventos de transporte de RutaNorte. Deja fuera devoluciones internacionales, pedidos telefónicos y predicción de retrasos. Añade que no almacena datos de tarjeta.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Proyecto_conjunto_Faro_Nido.docx — página 1`

**Evaluación:** **Correcta.** Las fuentes de reglas generales y del proyecto Faro eran adicionales e irrelevantes.

### Pregunta 2

**Pregunta:** ¿Qué ocurre cuando Atlas recibe dos veces el mismo `event_id` o un evento con una secuencia menor?

**Respuesta del RAG:** acepta un `event_id` repetido sin generar una segunda transición; archiva un evento con secuencia menor como tardío y no reemplaza el estado actual.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Proyecto_conjunto_Faro_Nido.docx — página 1`

**Evaluación:** **Correcta.** La fuente adicional de Faro no era necesaria.

### Pregunta 3

**Pregunta:** ¿Qué métricas debe cumplir el piloto y qué umbral activa el rollback?

**Respuesta del RAG:** indicó que el 99 % de los cambios de estado debe mostrarse en menos de 60 segundos y que una búsqueda de pedido debe tardar menos de dos segundos. Activaría rollback si la tasa de errores supera el 2 % durante cinco minutos o si el retraso de cola supera los 10 minutos.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Proyecto_conjunto_Faro_Nido.docx — página 1`

**Evaluación:** **Parcialmente correcta e incompleta.** Los umbrales de rollback son correctos. La métrica de 99 % debe cumplirse durante siete días consecutivos. Además, omitió tres criterios de aceptación: menos del 0,1 % de eventos en la cola de errores; p95 inferior a dos segundos para líneas temporales de hasta 200 eventos; cero duplicados visibles tras tres reintentos; y completar una prueba de recuperación antes de habilitar el segundo almacén. La respuesta mezcla el objetivo general de consulta rápida con los criterios formales de aceptación.

## 5. Proyecto conjunto Faro / Nido — usuario `tec`

**Acceso declarado:** departamento técnico. El documento está pensado para un trabajo conjunto de Ingeniería y Marketing, por lo que la consulta técnica es pertinente.

### Pregunta 1

**Pregunta:** ¿Qué cuatro zonas lumínicas devuelve Faro y qué alternativa se ofrece si no se puede usar el sensor del teléfono?

**Respuesta del RAG:** enumeró luz baja, indirecta suave, indirecta intensa y sol directo; afirmó que no se especifica alternativa si no se puede usar el sensor.

**Fuentes mostradas en la captura:**

- `Proyecto_conjunto_Faro_Nido.docx — página 1`
- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Parcialmente correcta, con una afirmación incorrecta.** Las cuatro zonas son correctas. Sí existe alternativa: seleccionar manualmente la zona cuando el navegador no ofrece sensor o la persona rechaza el permiso.

### Pregunta 2

**Pregunta:** ¿Qué datos registra la analítica y qué información de luz se procesa únicamente en el navegador?

**Respuesta del RAG:** enumeró zona lumínica, campaña, identificador de sesión aleatorio, fecha y hora UTC, además de eventos de inicio, elección de permiso, selección manual y visualización de recomendaciones. Añadió que la lectura del sensor se procesa en el navegador, no se envía ni se guarda como lectura bruta, y que no se registra ubicación precisa.

**Fuentes mostradas en la captura:**

- `Proyecto_conjunto_Faro_Nido.docx — página 1`
- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Parcialmente correcta.** La parte sobre medición de luz y ubicación es correcta. La lista de eventos está incompleta: también incluye guardar la guía por correo (`guide_email_opt_in`) y clic en catálogo (`catalog_click`).

### Pregunta 3

**Pregunta:** ¿Cuáles son las metas del piloto para la conversión a catálogo y el tiempo de carga móvil?

**Respuesta del RAG:** dijo que el contexto no especifica las metas numéricas y habló de la revisión y expansión a otras ciudades.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md — página 1`
- `Proyecto_conjunto_Faro_Nido.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Incorrecta.** El documento establece conversión desde recomendación a clic de catálogo de al menos 22 % y carga móvil p75 inferior a 2,5 segundos.

## 6. Propuesta de Marketing — usuario `mk`

**Acceso declarado:** departamento de Marketing. Las consultas corresponden a la propuesta de marketing y ventas de Círculo Verde.

### Pregunta 1

**Pregunta:** ¿Qué incluyen los planes mensual y trimestral, y cuánto cuesta cada uno?

**Respuesta del RAG:** plan mensual de 29 €, con planta, maceta estándar y ficha de cuidados; plan trimestral de 81 €, con lo mismo y una consulta de 15 minutos con una especialista.

**Fuentes mostradas en la captura:**

- `Propuesta_marketing_Circulo_Verde.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Correcta.** Las fuentes de reglas generales eran irrelevantes.

### Pregunta 2

**Pregunta:** ¿Cómo se distribuye el presupuesto de 28.000 € entre medios, creadores, producción y CRM?

**Respuesta del RAG:** afirmó que el contexto no incluía el desglose del presupuesto.

**Fuentes mostradas en la captura:**

- `Propuesta_marketing_Circulo_Verde.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Proyecto_conjunto_Faro_Nido.docx — página 1`

**Evaluación:** **Incorrecta.** La propuesta distribuye 14.400 € en medios pagados, 7.200 € en creadores, 5.000 € en producción y 1.400 € en CRM y medición.

### Pregunta 3

**Pregunta:** ¿Qué coste por compra se prevé para medios pagados y para la inversión completa, con una meta de 1.200 altas?

**Respuesta del RAG:** dijo que no había un coste concreto para medios pagados y que para la inversión completa el objetivo era mantener un CPA combinado inferior a 34 € con 1.200 compras.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Propuesta_marketing_Circulo_Verde.docx — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Incorrecta e incompleta.** La propuesta indica un CPA previsto de 12 € en medios pagados y 23,33 € considerando la inversión completa. El objetivo inferior a 34 € es el límite de campaña, no el cálculo solicitado.

## Hallazgos transversales

Las fuentes indicadas por pregunta reproducen los nombres y páginas visibles en las capturas; se conservan también las fuentes irrelevantes que el RAG mostró. En las capturas recortadas al borde inferior solo se incluyen las filas de fuentes que alcanzan a verse.

- **Respuestas correctas:** vacaciones; las dos primeras preguntas del CV salvo el filtrado de fuentes; las tres preguntas de RR. HH.; las dos primeras de Atlas; y la primera de Marketing.
- **Fallos de recuperación con respuestas de ausencia incorrectas:** horario estándar; datos de estudios, idiomas y herramientas del CV; alternativa manual de Faro; metas numéricas de Faro; desglose de presupuesto y CPA de Marketing. En varios casos, el RAG afirma que el documento no contiene información que sí aparece en el archivo.
- **Páginas y fragmentos:** en Faro, las respuestas de alternativa manual y objetivos numéricos citan principalmente la página 1, mientras que el detalle relevante aparece en la página 2. En Marketing, las respuestas de presupuesto y CPA citan la propuesta en página 1, pero el desglose aparece en página 2. Esto apunta a revisar el troceado, solapamiento, `top-k` y asociación entre fragmentos y páginas.
- **Fuentes irrelevantes:** en varios lotes aparecen documentos de reglas generales, CV, Atlas o Faro aunque no sean necesarios para la pregunta. Conviene revisar ranking y filtrado de resultados y que las fuentes mostradas respalden realmente cada afirmación.
- **Formato:** varias capturas muestran `**negrita**` literalmente, en lugar de renderizar el Markdown. Conviene revisar el formato de salida del prompt o el renderizador de la interfaz. En el lote conjunto Faro se usaron viñetas sin ese problema.
- **Control de acceso:** las pruebas de `rrhh`, `tec` y `mk` muestran recuperación positiva con usuarios que tienen el departamento correspondiente. `prueba` consultó reglas generales y su propio CV. No se ha mostrado una prueba negativa que confirme que un usuario sin autorización no puede recuperar el documento restringido de RR. HH. ni sus fuentes.


