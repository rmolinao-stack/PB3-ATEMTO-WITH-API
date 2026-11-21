# Memoria del proyecto de MLOps y API

En este apartado se describen los detalles relacionados con la construcción de la API y MLOps.

## Arreglos/modificaciones proyecto anterior de multiagente:

En este apartado se describen los arreglos y mejoras que se han realizado sobre la versión anterior de **ATeMto** para este proyecto:

* Se arreglan los errores tipográficos indicados en la evaluación del anterior proyecto. Concretamente: Nombre de la presentación, ficheros init en la estructura de carpetas, nombre incorrecto del repo.
* Se ha añadido `override=True` a `load_dotenv` para garantizar que las variables se cargan siempre. Esto se debe a que `load_dotenv` se invoca en varios ficheros (`common/config.py`, `common/cargar_api_key.py` y `multiagent/tools/api_tiempos_tmb.py`) y, para garantizar que siempre prevalezca el valor del `.env`, se fuerza la sobreescritura. Como mejora, `config.py` debería ser el único sitio donde se carguen variables de entorno, y el resto de módulos deberían leerlas desde `config`, pero esto queda fuera del alcance actual.
* Se eliminan algunos prints de control que no tienen sentido en producción.
* Se sustituyen los restos de SQLite (comentarios y docstrings) por PostgreSQL, que es la BBDD real del proyecto.

## Docker

Tanto para la API como para PostgreSQL se ha utilizado Docker. Docker ofrece la ventaja de tener los entornos en una misma máquina de forma aislada y sobre todo un mayor control y facilidad para CI/CD.

A continuación se indican las instrucciones utilizadas para construir las imágenes (y posterior contenedor en funcionamiento).

### API

Crear imagen: 
```text
docker build -t atemto-image .
```
Arrancar contenedor en primer plano:
```text 
docker run --rm --name atemto-container -p 8000:8000 --env-file .env atemto-image
```

### Postgres

Descarga de la imagen oficial y arranque del contenedor:

```text
docker run --name postgres-atemto -e POSTGRES_USER=EL_USUARIO -e POSTGRES_PASSWORD=EL_PASSWORD -e POSTGRES_DB=NOMBRE_DB -p 5432:5432 -d postgres
```
Hay que sustituir las variables con los datos correctos.

Para que la API use esta BBDD hay que informar `DATABASE_URL` en el `.env`. Si la API se ejecuta con `uvicorn` directamente en la máquina, el host es `localhost`. Si la API se ejecuta en un contenedor Docker, `localhost` apunta al propio contenedor, así que en Docker Desktop hay que usar `host.docker.internal` (o poner ambos contenedores en la misma red Docker y usar el nombre del contenedor, `postgres-atemto`). Por ejemplo:

```text
DATABASE_URL=postgresql://EL_USUARIO:EL_PASSWORD@host.docker.internal:5432/NOMBRE_DB
```

## Gráfico del sistema desplegado

![Sistema desplegado: front, API, PostgreSQL y LLM](../img/sistema_desplegado.svg)

* **Front (PB3-ATEMTO-API-CLIENT)**: cliente externo a este proyecto. Consume la API por HTTP/JSON enviando `api_key`.
* **API ATeMto**: contenedor Docker con FastAPI (desplegado en Render), que incluye el multiagente LangGraph y el RAG de tarifas (ChromaDB).
* **PostgreSQL**: contenedor Docker (desplegado en Render) donde se guarda el historial de mensajes por `thread_id`.
* **LLM**: Google Gemini, al que accede la API por HTTPS.
* **API TMB iMetro**: servicio externo al que consulta la tool de tiempos de llegada del metro.

## Contrato - EndPoints

La documentación interactiva (Swagger) está en `/docs` y `/` redirige a ella.

| Método | Ruta | Descripción | Requiere `api_key` |
|--------|------|-------------|:------------------:|
| GET | `/health` | Estado del servicio y motor de BBDD usado | No |
| POST | `/ask` | Envía una pregunta a ATeMto y devuelve su respuesta | Sí |
| POST | `/approve` | Aprueba o rechaza un plan pendiente de confirmación (HITL) | Sí |
| GET | `/threads/{thread_id}/messages` | Devuelve el historial de una conversación desde la BBDD | Sí |

### Autenticación y límites

* Los endpoints protegidos reciben la clave como parámetro de query `?api_key=...`, que debe coincidir con `API_KEY` del `.env` del servidor.
* Cada clave puede hacer como máximo `RATE_LIMIT_PER_MINUTE` peticiones en 60 s.
* Cada turno del agente tiene un tiempo máximo de `ASK_TIMEOUT_SECONDS`.

### GET /health

Público, sin `api_key`.

```json
{ "status": "ok", "storage": "postgresql" }
```

### POST /ask

Ejecuta un turno del agente. Al terminar el turno (sin plan pendiente), guarda la pregunta y la respuesta en la BBDD.

Body (JSON):

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `pregunta` | string | Sí | Pregunta del usuario (1-20000 caracteres, `MAX_PREGUNTA_CHARS` en `common/config.py`) |
| `thread_id` | string | No | Identificador de la conversación (máx. 100 caracteres). Por defecto `default`. Reutilizarlo mantiene el contexto |
| `auto_aprobar` | boolean | No | Por defecto `true`: si el agente deja un plan pendiente de aprobación, se aprueba automáticamente |

```text
curl -X POST "http://127.0.0.1:8000/ask?api_key=mi_api_key" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuánto tarda el próximo metro en Catalunya?", "thread_id": "thread-1"}'
```

### POST /approve

Aprueba o rechaza el plan pendiente de un hilo. Solo tiene sentido si `/ask` se llamó con `auto_aprobar: false` y devolvió `pendiente_hitl: true`.

Body (JSON):

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `thread_id` | string | Sí | Hilo con el plan pendiente (1-100 caracteres) |
| `aprobado` | boolean | Sí | `true` aprueba el plan; `false` lo rechaza |

```text
curl -X POST "http://127.0.0.1:8000/approve?api_key=mi_api_key" \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "thread-1", "aprobado": true}'
```

### Respuesta de /ask y /approve

```json
{
  "respuesta": "texto generado por ATeMto",
  "thread_id": "thread-1",
  "done": true,
  "pendiente_hitl": false,
  "error": null
}
```

* `respuesta`: texto de respuesta del agente.
* `thread_id`: hilo al que pertenece la respuesta.
* `done`: indica si el workflow ha terminado.
* `pendiente_hitl`: `true` si queda un plan pendiente de aprobar mediante `/approve`.
* `error`: mensaje de error del agente, o `null`.

### GET /threads/{thread_id}/messages

Devuelve la lista de mensajes guardados en la BBDD para el hilo.

```text
curl "http://127.0.0.1:8000/threads/thread-1/messages?api_key=mi_api_key"
```

```json
[
  { "role": "user", "content": "pregunta", "created_at": "2026-01-01T10:00:00" },
  { "role": "assistant", "content": "respuesta", "created_at": "2026-01-01T10:00:05" }
]
```

### Códigos de error

| Código | Cuándo |
|:------:|--------|
| 400 | `/ask` con una pregunta que queda vacía tras quitar espacios (por ejemplo, solo espacios), o `/approve` sin plan pendiente en el hilo |
| 401 | `api_key` ausente o inválida |
| 404 | `/approve` sobre un `thread_id` sin sesión (hay que llamar antes a `/ask`) |
| 422 | Body o parámetros que no cumplen el contrato (validación), por ejemplo `pregunta` vacía (`""`) o más larga de lo permitido, o `thread_id` de más de 100 caracteres |
| 429 | Se supera `RATE_LIMIT_PER_MINUTE` |
| 503 | El servidor no tiene `API_KEY` configurada |
| 504 | El turno del agente supera `ASK_TIMEOUT_SECONDS` |

## Datos

### Qué hay en PostgreSQL

Solo se persiste el historial de conversaciones. Las tablas las crea la propia API al arrancar (`SQLModel.metadata.create_all`, si no existen) y se definen en [models.py](../database/models.py).

| Tabla | Columnas | Descripción |
|-------|----------|-------------|
| `conversation` | `id` (PK, el `thread_id` del cliente, máx. 100), `created_at` (UTC) | Un hilo de conversación |
| `message` | `id` (PK autoincremental), `thread_id` (FK a `conversation.id`, indexado), `role` (`user` o `assistant`), `content`, `created_at` (UTC) | Cada pregunta y cada respuesta del hilo |

Reglas de escritura y lectura:

* Cada turno completado guarda dos filas en `message`: la pregunta (`user`) y la respuesta (`assistant`). La `conversation` se crea la primera vez que aparece el `thread_id`.
* Solo se guarda cuando el turno ha terminado y hay respuesta. Si el turno queda pendiente de aprobación (`pendiente_hitl: true`), no se guarda nada hasta que se llame a `/approve`.
* Solo se guardan la pregunta y la respuesta finales. No se guardan el plan, la traza, las llamadas a tools ni el estado del grafo.
* La BBDD solo se usa para consultar el historial (`GET /threads/{thread_id}/messages`). El agente no la lee para reconstruir su contexto.

### Qué se pierde si el proceso se reinicia

El estado del agente vive en la RAM del proceso de la API, no en PostgreSQL:

| Dato en memoria | Dónde | Efecto del reinicio |
|-----------------|-------|---------------------|
| Checkpoints del grafo LangGraph por `thread_id` (`MemorySaver`) | `multiagent/graph.py` | Se pierde el estado del grafo de cada hilo, incluidos los planes pendientes de aprobación (HITL) |
| Sesiones por hilo (`_sessions`) y última pregunta (`_last_pregunta`) | `api/app_api.py` | Se pierde el estado de cada hilo en la API |
| Contadores del rate limit | `api/rate_limit.py` | Vuelven a 0 |

Consecuencias prácticas:

* **Historial**: se conserva. Todo lo que ya se guardó en PostgreSQL se sigue pudiendo consultar con `GET /threads/{thread_id}/messages`.
* **Planes pendientes**: si había un turno esperando `/approve`, tras el reinicio `/approve` devuelve 404. Ese turno nunca se guardó en PostgreSQL, así que se pierde y el cliente debe repetir la pregunta.
* **Contexto del agente**: si el cliente sigue usando el mismo `thread_id`, el agente empieza con estado limpio, aunque el historial siga en PostgreSQL y se pueda consultar.
* **Rate limit**: tras un reinicio se pueden volver a hacer todas las peticiones permitidas por minuto.

El reinicio ocurre, por ejemplo, en cada deploy de Render o cuando Render reinicia el servicio. Además, estos datos no se comparten entre procesos: con varios workers o varias instancias, cada uno tendría su propio `MemorySaver`.

Limitaciones conocidas:

* Los entornos DEV y PRO usan la misma base de datos, por lo que un mismo `thread_id` en ambos escribe en la misma conversación.
* Si el cliente no envía `thread_id`, se usa `default`, que es compartido por todos los clientes que lo omitan. Por tanto, esos clientes comparten contexto e historial.

## Entornos de despliegue (Render)

Tanto la API como la BBDD están desplegadas en Render.

La API dispone de dos entornos:

* **DEV (desarrollo)**: Apunta a la rama develop de GitHub y sirve para ir verificando el desarrollo sobre un entorno lo más realista posible a producción. La URL debe consultarse con el responsable del proyecto.
* 
* **PRO (producción)**: Apunta a la rama main de GitHub y es el producto final. La URL debe consultarse con el responsable del proyecto.

Por un tema de limitación de recursos solo hay un entorno de BBDD PostgreSQL en Render, y los dos entornos apuntan a la misma BBDD.

No se entrega la URL de la BBDD porque la conexión es interna.

## Prueba de vida

La prueba de vida comprueba que el historial sobrevive a un redeploy, es decir, que los datos están en PostgreSQL y no en la memoria de la API:

1. **Turno**: se hace un `POST /ask` con un `thread_id` de prueba (por ejemplo `thread-1`) y se verifica que la API responde con `200` y una `respuesta`.
2. **Redeploy**: se hace un push a la rama del entorno (`develop` para DEV, `main` para PRO) y Render despliega de nuevo. El proceso se reinicia, por lo que se pierden `MemorySaver`, las sesiones y los contadores del rate limit.
3. **GET**: se llama a `GET /threads/thread-1/messages` y el historial sigue ahí, con la pregunta (`user`) y la respuesta (`assistant`) del turno anterior.

Con esto se confirma lo descrito en el apartado "Datos": tras un reinicio se pierde el estado del agente, pero el historial persiste en PostgreSQL. Además, `GET /health` devuelve `"storage": "postgresql"`, lo que confirma que la API está usando la base de datos y no un fichero local.

## Conclusiones de arquitectura y costes

**Piezas.** El front (PB3-ATEMTO-API-CLIENT) es un cliente externo que se ejecuta en local y llama a la API por HTTP. En Render hay un Web Service con la API, el multiagente y el RAG, y una base de datos PostgreSQL. La API, el agente y el RAG van en un solo contenedor porque comparten proceso y código: el agente invoca el RAG como una tool, así que separarlos solo añadiría llamadas de red, otro despliegue y otra factura sin un beneficio claro a esta escala. El estado del agente vive en memoria y solo el historial va a PostgreSQL (ver apartado "Datos").

**Límite notado: cold start.** Ambos servicios usan el plan Free de Render. Con ese plan el Web Service se duerme tras un tiempo sin tráfico, y la primera petición después de la inactividad tardó más de 30 segundos mientras el contenedor arrancaba. En la demo se notó como una primera respuesta muy lenta, y las siguientes ya iban con normalidad. La solución práctica es lanzar un `GET /health` unos minutos antes de empezar. Como el arranque reinicia el proceso, además se pierde el estado en memoria (ver "Datos").

**Escalado.** El primer paso si hubiera más usuarios sería subir el Web Service a un plan de pago: evita que se duerma, y da más RAM y CPU. Lo mismo para PostgreSQL, que en el plan Free tiene límites de tamaño y caducidad. No montaríamos varias réplicas ni colas de tareas: el `MemorySaver`, las sesiones y el rate limit viven en la RAM de cada proceso, y con varias réplicas cada una tendría su propio estado. Para escalar así habría que externalizar ese estado (por ejemplo, a un checkpointer en PostgreSQL y un rate limit en Redis).

**Factura de infraestructura (web + Postgres).** Hoy es de 0 €/mes, porque ambos servicios usan el plan Free. En un plan de pago de entrada, el orden de magnitud sería de unos 10-15 USD/mes en total (alrededor de 7 USD el Web Service y 6 USD la base de datos; ver los precios actuales en render.com/pricing).

**Factura de tokens de un `/ask`.** Un `/ask` encadena varias llamadas al LLM (supervisor, especialista con tools, RAG y síntesis). Cada especialista puede hacer hasta 4 pasos modelo↔tools (`MAX_STEPS_DEFAULT`) y el supervisor se limita a 8 iteraciones (`MAX_ITER`). No se ha medido el consumo real. Hoy es 0 € porque usamos la cuota gratuita de Gemini, pero al ser una API pública sin control de gasto por usuario, el coste real es el riesgo descrito en "Cosas a mejorar" (clave por consumidor y LLM local).

## Conclusiones de CI/CD

* **Antes de cada deploy**: se prueba en local con Docker Desktop. Se hace un `docker build` y se arranca el contenedor con el `.env` local. Después se comprueba que la API está viva (`GET /health`, que no llama al LLM y muestra `"storage": "postgresql"`) y que las consultas a la BBDD funcionan (`GET /threads/{thread_id}/messages`). Así se detectan antes del push los errores de build, de dependencias o de conexión a la BBDD sin gastar tokens.
* **Secretos**: están en el panel de Render (variables de entorno del servicio) y en el `.env` en local. No van al repositorio porque `.env` está en `.gitignore` (y también en `.dockerignore`, así que no entra en la imagen), y en el código solo se sube `.env.example` con valores de ejemplo. Tampoco se escriben en los logs: la API nunca registra `API_KEY` ni `GEMINI_API_KEY`.
* **Despliegue**: se hace push a `develop` (entorno DEV) o a `main` (entorno PRO) y Render redespliega solo.
* **Rollback**: si un deploy sale mal, se vuelve al deploy anterior que funcionaba desde el panel de Render (redeploy de un deploy previo), sin tocar el código. Después se corrige en git y se vuelve a desplegar. El historial en PostgreSQL no se ve afectado.
* **Desarrollo frente a producción**: lo que los separa es el entorno, no el código. En local se usa la máquina del desarrollador con su `.env`. En Render, cada servicio (DEV y PRO) apunta a su rama y tiene sus propias variables en el panel. La base de datos es la misma para ambos (ver "Entornos de despliegue").

## Cosas a mejorar

* **LLM local**: Al ser una API pública corremos el riesgo de gastar muchos tokens sin control. Una solución podría ser montar el servicio con un LLM local que no consuma tokens. Esto tiene varias implicaciones: hace falta una infraestructura propia (que podría estar en la nube) y su mantenimiento, hay costes indirectos (por ejemplo, alquiler de servidor o consumo eléctrico) y hay que asumir las limitaciones del LLM local seleccionado.
* **Key por consumidor (APP_KEY)**: Para mejorar el control de uso y la seguridad, se podría añadir una APP_KEY (como la de TMB) y mantenerla en la BBDD, de modo que cada consumidor tenga la suya y podamos saber quién hace las llamadas y cuáles. Esto exigiría cambiar el modelo de datos de conversaciones y mensajes.
* **Enviar la key por cabecera (`X-API-Key`)**: Para mejorar la seguridad, la clave no debería ir en la URL como parámetro de query, porque queda registrada en logs de proxies y en el historial de navegación. Lo ideal es enviarla en una cabecera.
* **Cargar variables de entorno solo en config**: Al heredar el código de proyectos anteriores, se ha detectado que `load_dotenv` se llama también fuera de `common/config.py` (en `common/cargar_api_key.py` y `multiagent/tools/api_tiempos_tmb.py`). Esto no es una buena práctica: hay varios puntos de carga y la precedencia de los valores puede variar. Se debería centralizar la carga en `config.py` y refactorizar el resto de módulos para que lean sus parámetros desde `config`.



