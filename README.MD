## ORM Avanzado (Laboratorio 7)

Se amplió el modelo de datos con tres campos nuevos, necesarios para aplicar las técnicas de este laboratorio sobre AgroTrace:
- `cupo_diario_lotes` (IntegerField) en `FundoProductor` — campo entero a descontar.
- `estado_evaluacion` (ya existente) en `LoteRecepcionado` — campo de estado (PENDIENTE, EN_PROCESO, PROCESADO).
- `costo_auditoria` (DecimalField) en `CertificacionLote` — atributo numérico del modelo intermedio N:M.

### Transacción atómica
`recepcion_transaccional` registra un `LoteRecepcionado` y descuenta `cupo_diario_lotes` de su `FundoProductor` dentro de una misma `transaction.atomic()`, usando `F()` para el descuento seguro. Si el fundo no tiene cupo disponible, la transacción completa se revierte (rollback probado: 0 cambios en cupo y conteo de lotes).

### Reportes (aggregate / annotate)
`reporte_general` expone tres reportes en `reporte.html` (hereda de `base.html`):
- Costo total/promedio de auditorías y cantidad de certificaciones, con `aggregate()` sobre `CertificacionLote`.
- Producción agrupada por `estado_evaluacion`, con `values().annotate()`.
- Total de lotes por fundo, con `annotate()` sobre `FundoProductor`.

### QuerySet personalizado
`LoteQuerySet` (en `models.py`) define `pendientes()` y `con_alto_descarte(umbral)`, encadenables y asignados a `LoteRecepcionado.objects` mediante `as_manager()`. Usado en `lote_list` y `reporte_general`.

### Optimización de consultas (N+1)
Se midió con `connection.queries` el listado de lotes: 7 consultas sin optimizar (N+1, para 6 lotes) frente a 2 consultas aplicando `select_related('fundo', 'evaluacion_calidad')` y `prefetch_related('certificaciones')`.

### Nuevas rutas
- `/agrotrace/recepcion-transaccional/` — registro transaccional de lotes.
- `/agrotrace/reporte/` — reporte consolidado de operaciones y métricas.