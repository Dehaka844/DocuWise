# Proyecto Atlas de trazabilidad de pedidos

**Área:** Ingeniería de Plataforma  
**Responsable:** Nuria Campos, Engineering Manager  
**Versión:** 1.4 · **Estado:** piloto interno  
**Última actualización:** 4 de noviembre de 2026

## Objetivo

Atlas ofrece una vista única del recorrido de cada pedido desde que se confirma el pago hasta que se entrega. El piloto integra los almacenes de Madrid y Valencia y alimenta el panel de Operaciones con eventos normalizados. El objetivo de servicio es mostrar el 99 % de los cambios de estado en menos de 60 segundos y permitir recuperar un pedido por su identificador en menos de dos segundos.

## Alcance del piloto

Incluye pedidos web de España, eventos de pago de PayRiver, preparación de almacén en StockPilot y eventos de transporte de RutaNorte. Quedan fuera las devoluciones internacionales, los pedidos telefónicos y la predicción de retrasos. Atlas no almacena datos de tarjeta: recibe únicamente el identificador de transacción y su estado.

## Arquitectura

1. **Entrada:** el API Gateway recibe webhooks firmados y aplica límite de 120 solicitudes por segundo por cliente.
2. **Cola:** Kafka, tópico `atlas.order-events.v1`, retención de 72 horas y clave de partición `order_id`.
3. **Normalización:** servicio Kotlin `atlas-normalizer` valida el esquema, convierte horas a UTC y asigna `event_id` idempotente.
4. **Persistencia:** PostgreSQL almacena el estado actual y el historial de cambios; Redis mantiene una caché de lecturas frecuentes durante 15 minutos.
5. **Consulta:** GraphQL expone `orderTimeline(orderId)` a la consola de Operaciones.
6. **Observabilidad:** OpenTelemetry exporta trazas y métricas a Grafana; los registros técnicos se conservan 30 días.

## Contrato de evento

| Campo | Tipo | Requisito | Ejemplo |
|---|---|---|---|
| `event_id` | UUID | Obligatorio, único | `7fa8...` |
| `order_id` | string | Obligatorio, máximo 32 caracteres | `LM-584219` |
| `source` | enum | `PAYRIVER`, `STOCKPILOT`, `RUTANORTE` | `STOCKPILOT` |
| `status` | enum | `PAID`, `PICKING`, `PACKED`, `SHIPPED`, `DELIVERED`, `EXCEPTION` | `PACKED` |
| `occurred_at` | RFC 3339 | Obligatorio, zona UTC | `2026-11-04T10:15:00Z` |
| `sequence` | integer | Monótono por pedido y fuente | `18` |

Los productores deben reintentar con espera exponencial ante respuestas 429 o 5xx. Un evento repetido con el mismo `event_id` se acepta y no genera una segunda transición. Un evento con secuencia menor se archiva como tardío y no reemplaza el estado actual.

## Seguridad y acceso

Los webhooks usan HMAC-SHA256 con rotación trimestral de secretos en Vault. Los servicios se autentican entre sí con identidad de carga de trabajo. Ingeniería de Plataforma administra el esquema y la infraestructura; Operaciones puede consultar pedidos, pero no cambiar estados ni consultar secretos. El entorno de pruebas usa identificadores generados y no replica tablas de clientes.

## Despliegue y recuperación

El despliegue se realiza en Kubernetes mediante Helm. El piloto usa dos réplicas del normalizador y tres particiones Kafka. Cada cambio requiere revisión de una persona distinta de quien lo implementó y despliegue primero en `staging`. El rollback se activa si la tasa de errores supera el 2 % durante cinco minutos o si el retraso de cola supera diez minutos.

PostgreSQL tiene copias incrementales cada hora y una copia completa diaria. El objetivo de recuperación es un RPO de 15 minutos y un RTO de dos horas. La persona de guardia de Plataforma coordina la recuperación y Operaciones valida que la línea temporal vuelva a estar completa.

## Métricas de aceptación

- 99 % de eventos visibles en menos de 60 segundos durante siete días consecutivos.
- Menos de 0,1 % de eventos en cola de errores; todo evento fallido incluye causa y fecha.
- Consulta p95 inferior a 2 segundos para una línea temporal de hasta 200 eventos.
- Ningún duplicado visible después de reintentar el mismo webhook tres veces.
- Prueba de recuperación completada antes de habilitar el segundo almacén.

## Hitos y responsables

| Hito | Fecha objetivo | Responsable | Dependencia |
|---|---|---|---|
| Congelar esquema v1 | 13 nov 2026 | Nuria Campos | Revisión de Operaciones |
| Prueba de carga | 20 nov 2026 | Iker Vidal | Datos de prueba de 1 M eventos |
| Simulacro de recuperación | 24 nov 2026 | Sara Gil | Copia y runbook |
| Piloto Madrid | 30 nov 2026 | Pablo Navas | Aprobación de Operaciones |

## Riesgos conocidos

**Eventos fuera de orden:** se usan `sequence` y `occurred_at`; la consola muestra una marca de evento tardío.  
**Caída de un proveedor:** la cola retiene eventos durante 72 horas y el conector reintenta.  
**Cambios de contrato sin aviso:** el gateway rechaza versiones desconocidas y envía alerta al canal `#atlas-integraciones`.

## Decisiones pendientes

1. Definir si el estado `EXCEPTION` debe exponer un código legible para atención al cliente.
2. Confirmar con Seguridad si las exportaciones CSV deben llevar marca de agua por usuario.
3. Decidir el criterio de retención del historial de pedidos una vez termine el piloto.
