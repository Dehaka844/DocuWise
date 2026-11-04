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

**Respuesta del RAG:** la empresa permite una entrada flexible entre las **08:00 y las 10:00**, siempre que se completen las horas de trabajo y se cubran las reuniones acordadas. Además, debe existir disponibilidad común del equipo entre las **10:00 y las 14:00**.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Parcialmente correcta.** La respuesta ya no afirma que el horario estándar no esté especificado y recoge correctamente la franja flexible y la disponibilidad común. Aun así, omite el horario estándar de 09:00 a 18:00 y la pausa de comida de 14:00 a 15:00.

### Pregunta 2

**Pregunta:** ¿Cuántos días laborables de vacaciones corresponden al año y con cuánta antelación deben solicitarse?

**Respuesta del RAG:** 25 días laborables por año natural; solicitud con al menos 10 días laborables de antelación mediante NexoPeople.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Correcta.** La respuesta y la fuente coinciden con la política de vacaciones.

### Pregunta 3

**Pregunta:** ¿Qué límites de gasto se aplican al alojamiento y a la compra de equipos, y quién debe aprobar las excepciones?

**Respuesta del RAG:** alojamiento hasta **150 € por noche en España**; las excepciones deben ser aprobadas por **Dirección antes de reservar**. En compra de equipos: hasta **300 €**, aprobación del **responsable**; de **301 a 2.000 €**, aprobación de **Dirección**; más de **2.000 €**, aprobación de **Dirección Financiera**. Además, las excepciones a estas reglas requieren **aprobación escrita del director de área**, con registro de su duración y motivo.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `CV_Claudia_Serrano_Vidal.docx — página null`

**Evaluación:** **Correcta y completa.** Incluye los topes, las aprobaciones de cada tramo y el requisito general de aprobación escrita del director de área, con registro de duración y motivo. El CV es una fuente irrelevante para esta consulta.

## 2. CV — usuario `prueba`

**Acceso declarado:** sin departamento; propietario del CV cargado. La consulta del propio CV es coherente con ese contexto.

### Pregunta 1

**Pregunta:** ¿En qué empresas trabajó Claudia, en qué puestos y durante qué periodos?

**Respuesta del RAG:** Claudia trabajó en Brújula Mobility como Senior Product Designer desde abril de 2022 hasta la actualidad.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página null`

**Evaluación:** **Incorrecta e incompleta.** Brújula Mobility y el puesto y periodo indicados son correctos, pero la respuesta omite AulaNube y Estudio Norte, que también forman parte de la trayectoria profesional de Claudia.

### Pregunta 2

**Pregunta:** ¿Qué resultados obtuvo al rediseñar el alta de conductores en Brújula Mobility?

**Respuesta del RAG:** redujo el abandono del alta de conductores del **31 % al 19 % en dos trimestres**.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página null`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** El resultado coincide con el CV; la fuente de reglas generales no aporta a esta respuesta.

### Pregunta 3

**Pregunta:** ¿Qué estudios, idiomas y herramientas aparecen en su perfil?

**Respuesta del RAG:** estudios: Máster en Diseño de Interacción en la Universitat Politècnica de València (2017–2018) y Grado en Comunicación Audiovisual en la Universidad de Alicante (2013–2017). Idiomas: español nativo, inglés C1 y valenciano B2. Herramientas: Figma y FigJam.

**Fuentes mostradas en la captura:**

- `CV_Claudia_Serrano_Vidal.docx — página null`

**Evaluación:** **Correcta y completa para lo preguntado.** Incluye los dos estudios, los tres idiomas y las dos herramientas que aparecen en el CV.

## 3. Información de Recursos Humanos — usuario `rrhh`

**Acceso declarado:** departamento de Recursos Humanos. Las tres preguntas eran sobre el documento restringido de RR. HH.

### Pregunta 1

**Pregunta:** ¿Qué ajuste salarial recibirá Elena Vázquez en enero de 2027 y cuál será su nueva compensación anual?

**Respuesta del RAG:** Elena Vázquez recibirá un ajuste salarial del **4,5 %** desde el **1 de enero de 2027**. Su nueva compensación anual será de **50.787 €**, siempre que firme la carta de revisión antes del **15 de diciembre de 2026**.

**Fuentes mostradas en la captura:**

- `Acceso_restringido_Recursos_Humanos.pdf — página 1`
- `Acceso_restringido_Recursos_Humanos.pdf — página 2`

**Evaluación:** **Correcta y más completa.** Añade correctamente la condición de firmar la carta de revisión antes del 15 de diciembre de 2026. La página 2 citada no parece necesaria para esta respuesta.

### Pregunta 2

**Pregunta:** ¿Cómo se pagará la prima de retención de Tomás Rueda y qué condición debe cumplir para recibir cada tramo?

**Respuesta del RAG:** Tomás Rueda recibirá una prima de retención total de **3.000 €**, pagada en dos tramos: **1.500 € en marzo de 2027** y **1.500 € en septiembre de 2027**. Para recibir cada tramo, debe **continuar en la empresa en la fecha correspondiente**.

**Fuentes mostradas en la captura:**

- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Acceso_restringido_Recursos_Humanos.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`
- `Acceso_restringido_Recursos_Humanos.pdf — página 2`

**Evaluación:** **Correcta.** La respuesta coincide con el documento de RR. HH. Las páginas de reglas generales y la página 2 del documento de RR. HH. son fuentes adicionales que no hacen falta para esta respuesta.

### Pregunta 3

**Pregunta:** ¿Quiénes son las tres personas candidatas a Data Analyst y qué puntuación técnica obtuvo cada una?

**Respuesta del RAG:** Clara Beltrán obtuvo **4,6/5**; Diego Pons, **4,2/5**; y Amina Ríos, **4,4/5**.

**Fuentes mostradas en la captura:**

- `Acceso_restringido_Recursos_Humanos.pdf — página 2`

**Evaluación:** **Correcta.** La respuesta y la única fuente mostrada son pertinentes para la pregunta.

## 4. Diseño técnico de Atlas — usuario `tec`

**Acceso declarado:** departamento técnico. El usuario consultó documentación de Ingeniería de Plataforma.

### Pregunta 1

**Pregunta:** ¿Qué servicios y fuentes de eventos integra el piloto de Atlas y cuáles quedan fuera de su alcance?

**Respuesta del RAG:** el piloto integra pedidos web de España, eventos de pago de PayRiver, eventos de preparación de almacén de StockPilot y eventos de transporte de RutaNorte. Deja fuera devoluciones internacionales, pedidos telefónicos y predicción de retrasos. Además, Atlas no almacena datos de tarjeta; recibe el identificador de transacción y su estado.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md`
- `Proyecto_conjunto_Faro_Nido.docx`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`

**Evaluación:** **Correcta.** La respuesta cubre las integraciones, las exclusiones y el tratamiento de los datos de tarjeta. La fuente de Atlas es pertinente; el proyecto Faro y las reglas generales son fuentes adicionales e irrelevantes.

### Pregunta 2

**Pregunta:** ¿Qué ocurre cuando Atlas recibe dos veces el mismo `event_id` o un evento con una secuencia menor?

**Respuesta del RAG:** si Atlas recibe dos veces el mismo `event_id`, acepta el evento, pero no genera una segunda transición. Si recibe un evento con una secuencia menor, lo archiva como tardío y no reemplaza el estado actual.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md`

**Evaluación:** **Correcta.** La respuesta y la única fuente mostrada son pertinentes.

### Pregunta 3

**Pregunta:** ¿Qué métricas debe cumplir el piloto y qué umbral activa el rollback?

**Respuesta del RAG:** enumeró metas de Faro (inicio a resultado ≥ 70 %, resultado a clic de catálogo ≥ 22 %, carga móvil p75 < 2,5 segundos, investigar el uso de la alternativa manual si supera 45 % e incidencias de recomendación incorrecta < 3 por cada 100 sesiones revisadas) y objetivos de servicio de Atlas (99 % de cambios en menos de 60 segundos y recuperar un pedido en menos de 2 segundos). Afirmó que no se especifica un umbral explícito de rollback y citó acciones operativas de Faro: pausar anuncios si menos del 90 % de recomendaciones tiene alternativa, abrir incidencia prioritaria si los errores superan el 5 % de las sesiones y desactivar la medición ante exposición de datos.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md`
- `Proyecto_conjunto_Faro_Nido.docx`

**Evaluación:** **Parcialmente correcta, con una afirmación incorrecta sobre el rollback.** Las metas de conversión, carga, uso manual e incidencias corresponden a Faro; los objetivos de servicio corresponden a Atlas. Sin embargo, Atlas sí define rollback: tasa de errores superior al 2 % durante cinco minutos o retraso de cola superior a 10 minutos. Las acciones de Faro sobre anuncios, incidencias y medición son medidas operativas distintas, no sustituyen el umbral de rollback de Atlas. La respuesta también omite que el 99 % de los cambios debe mostrarse en menos de 60 segundos durante siete días consecutivos y varios criterios de aceptación de Atlas: menos del 0,1 % de eventos en cola de errores, consulta p95 inferior a 2 segundos para hasta 200 eventos, ausencia de duplicados tras tres reintentos y prueba de recuperación antes de habilitar el segundo almacén. Las fuentes citadas son pertinentes para los datos mezclados, pero la respuesta confunde las métricas de dos proyectos.

## 5. Proyecto conjunto Faro / Nido — usuario `tec`

**Acceso declarado:** departamento técnico. El documento está pensado para un trabajo conjunto de Ingeniería y Marketing, por lo que la consulta técnica es pertinente.

### Pregunta 1

**Pregunta:** ¿Qué cuatro zonas lumínicas devuelve Faro y qué alternativa se ofrece si no se puede usar el sensor del teléfono?

**Respuesta del RAG:** enumeró luz baja, indirecta suave, indirecta intensa y sol directo. Si no se puede usar el sensor del teléfono, prioriza la selección manual y aclara que no se especifica más detalle sobre cómo realizarla.

**Fuentes mostradas en la captura:**

- `Proyecto_conjunto_Faro_Nido.docx`

**Evaluación:** **Correcta.** Identifica las cuatro zonas y la alternativa manual. El documento no detalla más el procedimiento, como indica la respuesta.

### Pregunta 2

**Pregunta:** ¿Qué datos registra la analítica y qué información de luz se procesa únicamente en el navegador?

**Respuesta del RAG:** indicó que el contexto no especifica qué datos registra la analítica ni qué información de luz se procesa únicamente en el navegador.

**Fuentes mostradas en la captura:**

- `Proyecto_conjunto_Faro_Nido.docx`

**Evaluación:** **Incorrecta.** El documento sí especifica que la analítica registra la zona lumínica, la campaña, un identificador aleatorio de sesión, la fecha en UTC y los eventos `faro_start`, `light_permission_choice`, `manual_zone_selected`, `recommendation_view`, `guide_email_opt_in` y `catalog_click`. La lectura del sensor se procesa en el navegador; la lectura bruta de lux no se envía ni se registra, y tampoco se registra ubicación precisa.

### Pregunta 3

**Pregunta:** ¿Cuáles son las metas del piloto para la conversión a catálogo y el tiempo de carga móvil?

**Respuesta del RAG:** indicó una conversión de resultado a clic en el catálogo del **22 % o más** y un tiempo de carga p75 en móvil de **menos de 2,5 segundos**.

**Fuentes mostradas en la captura:**

- `Diseno_tecnico_Proyecto_Atlas.md`
- `Proyecto_conjunto_Faro_Nido.docx`

**Evaluación:** **Correcta.** Ambas metas coinciden con los indicadores del proyecto Faro. La fuente de Atlas es adicional e irrelevante; las fuentes aparecen sin número de página en la captura.

## 6. Propuesta de Marketing — usuario `mk`

**Acceso declarado:** departamento de Marketing. Las consultas corresponden a la propuesta de marketing y ventas de Círculo Verde.

### Pregunta 1

**Pregunta:** ¿Qué incluyen los planes mensual y trimestral, y cuánto cuesta cada uno?

**Respuesta del RAG:** el plan mensual cuesta **29 €** e incluye una planta, una maceta estándar y una guía de cuidados. El plan trimestral cuesta **81 €** e incluye tres entregas y una consulta de cuidado de 15 minutos con una especialista.

**Fuentes mostradas en la captura:**

- `Propuesta_marketing_Circulo_Verde.docx`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** La respuesta coincide con la propuesta. Las reglas generales son una fuente adicional e irrelevante.

### Pregunta 2

**Pregunta:** ¿Cómo se distribuye el presupuesto de 28.000 € entre medios, creadores, producción y CRM?

**Respuesta del RAG:** distribuyó los **28.000 €** en 14.400 € para medios pagados, 7.200 € para creadores, 5.000 € para producción y 1.400 € para CRM y medición; totalizó 28.000 €.

**Fuentes mostradas en la captura:**

- `Propuesta_marketing_Circulo_Verde.docx`
- `Reglas_generales_Lumenia_Labs.pdf — página 1`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** El desglose y la suma coinciden con la propuesta. Las dos fuentes de reglas generales son adicionales e irrelevantes.

### Pregunta 3

**Pregunta:** ¿Qué coste por compra se prevé para medios pagados y para la inversión completa, con una meta de 1.200 altas?

**Respuesta del RAG:** con 1.200 altas, prevé **12,00 € por compra en medios pagados** y **23,33 € por compra considerando la inversión completa**.

**Fuentes mostradas en la captura:**

- `Propuesta_marketing_Circulo_Verde.docx`
- `Reglas_generales_Lumenia_Labs.pdf — página 2`

**Evaluación:** **Correcta.** Ambos importes coinciden con el CPA previsto en la propuesta. Las reglas generales son una fuente adicional e irrelevante.

## Hallazgos transversales

Las fuentes indicadas por pregunta reproducen los nombres y páginas visibles en las capturas; se conservan también las fuentes irrelevantes que el RAG mostró. En las capturas recortadas al borde inferior solo se incluyen las filas de fuentes que alcanzan a verse.

- **Respuestas correctas:** vacaciones; las preguntas 2 y 3 del CV; las tres preguntas de RR. HH.; las dos primeras de Atlas; las preguntas 1 y 3 del lote 5; y las tres preguntas de Marketing.
- **Respuestas incompletas o incorrectas:** horario estándar omitido; trayectoria profesional del CV incompleta en la pregunta 1 del lote 2; en el lote 4 se mezclan métricas de Faro con las de Atlas y se niega erróneamente que Atlas tenga umbrales de rollback; en la pregunta 2 del lote 5 el RAG afirma incorrectamente que no hay datos sobre analítica, aunque sí están en Faro. En varios casos, el RAG afirma que el documento no contiene información que sí aparece en el archivo.
- **Páginas y fragmentos:** en las capturas nuevas de los lotes 5 y 6, los documentos Faro y Marketing aparecen sin número de página, así que no se puede comprobar desde la interfaz qué página o fragmento se recuperó. Conviene revisar el troceado, solapamiento, `top-k` y asociación entre fragmentos y páginas.
- **Fuentes irrelevantes:** en varios lotes aparecen documentos de reglas generales, CV, Atlas o Faro aunque no sean necesarios para la pregunta. Conviene revisar ranking y filtrado de resultados y que las fuentes mostradas respalden realmente cada afirmación.
- **Formato:** varias capturas muestran `**negrita**` literalmente, en lugar de renderizar el Markdown. Conviene revisar el formato de salida del prompt o el renderizador de la interfaz. En el lote conjunto Faro se usaron viñetas sin ese problema.
- **Control de acceso:** las pruebas de `rrhh`, `tec` y `mk` muestran recuperación positiva con usuarios que tienen el departamento correspondiente. `prueba` consultó reglas generales y su propio CV. No se ha mostrado una prueba negativa que confirme que un usuario sin autorización no puede recuperar el documento restringido de RR. HH. ni sus fuentes.


