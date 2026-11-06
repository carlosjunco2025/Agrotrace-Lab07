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

## Laboratorio 9 — Frontend React con Vite

La aplicación React del laboratorio está en `frontend/`. Requiere Node.js y npm instalados:

```bash
node -v
npm -v
cd frontend
npm install
npm run dev
```

Vite muestra la URL local en la terminal (por defecto `http://localhost:5173`). Para comprobar el código y generar la versión de producción:

```bash
npm run lint
npm run build
```

El panel inicial usa datos mock en `frontend/src/App.jsx`; todavía no realiza solicitudes HTTP al backend.

### Estructura: Django y React

| Aspecto | Python / Django | JavaScript / React + Vite |
|---|---|---|
| Lenguaje | Python | JavaScript (JSX para describir la interfaz) |
| Gestor de paquetes | `pip` | `npm` |
| Archivo de dependencias | `requirements.txt` | `package.json` (versiones resueltas en `package-lock.json`) |
| Carpeta de dependencias | `.venv/` | `node_modules/` |
| Servidor de desarrollo | `python manage.py runserver` | `npm run dev` |

`frontend/index.html` es el documento de entrada y contiene el elemento `#root`; puede compararse con la plantilla base `base.html`, aunque aquí solo es la carcasa de una aplicación de una página. `src/main.jsx` crea el punto de montaje de React en el navegador; inicia la aplicación cliente, pero no sustituye literalmente a `wsgi.py` ni a `urls.py`, que son infraestructura y enrutamiento del servidor Django. `src/App.jsx` define la vista y los componentes que React renderiza; en términos de presentación cumple un propósito parecido a una plantilla MVT alimentada por una vista (`views.py`), pero el renderizado ocurre en el cliente. `package.json` declara scripts y dependencias como hace `requirements.txt` con las dependencias Python. `node_modules/` contiene paquetes instalados, análogo a `.venv/`; normalmente ambos directorios se excluyen del control de versiones.

### Renderizado y relación entre los datos

En React, `fundos.map(...)` y el `.map(...)` interno de lotes transforman arreglos JavaScript en elementos de interfaz en el navegador (CSR); React exige una `key` estable para cada elemento listado. En una plantilla Django, `{% for item in items %}` itera sobre el contexto que el servidor preparó y genera HTML en el servidor (SSR). Ambos recorren colecciones, pero se ejecutan en entornos distintos.

Con los Templates de la Semana 6, Django recibe una petición, consulta los datos, renderiza el HTML y devuelve una página; una navegación suele volver al servidor. En una SPA React, el servidor entrega el HTML inicial y los archivos JavaScript; React construye y actualiza la interfaz en el navegador. Los datos pueden cambiar sin recargar todo el documento, normalmente mediante solicitudes a una API. React no reemplaza la API ni los modelos de Django.

### ¿Qué falta para conectar React con la API de la Semana 8?

1. Reemplazar los arreglos mock por estado React (`useState`) y cargar `/api/fundos/` y `/api/lotes/` en un `useEffect` al montar la aplicación.
2. Ejecutar las solicitudes mediante `fetch` (incluyendo la comprobación de `response.ok`, estados de carga y errores) o instalar y configurar `axios`. Los endpoints actuales están declarados en `agrotrace_config/urls.py` y aceptan listados DRF; los serializadores entregan fundos y lotes simples por separado, con `lote.fundo` como ID. La interfaz debe asociar el lote con el fundo cuyo `id` coincide.
3. Como Vite y Django suelen ejecutarse en puertos distintos, permitir el origen del frontend en Django con `django-cors-headers`: instalar el paquete, añadir `corsheaders` a `INSTALLED_APPS`, agregar `corsheaders.middleware.CorsMiddleware` antes de `django.middleware.common.CommonMiddleware` y declarar, por ejemplo, `CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]`. Alternativamente, se puede configurar un proxy de desarrollo de Vite.
4. Añadir manejo de estados de carga, error y respuesta vacía. Para operaciones que modifican datos, además se deben atender el método HTTP, validación y protección CSRF según la configuración del backend.

`node_modules/` y `dist/` no deben versionarse; ambos están excluidos por el `.gitignore` de la raíz. Sí se versionan `package.json` y, una vez generado con `npm install`, `package-lock.json` para reproducir las dependencias.