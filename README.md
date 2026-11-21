# ATeMto (With API)

***PB3-ATEMTO-WITH-API*** *es una ampliación de **ATeMto**: incluye todas las funcionalidades originales y añade una API para que otros clientes puedan consumirlo de forma remota e interactuar con algunas de sus funcionalidades internas, enriqueciendo así sus propios sistemas.*

En general, **ATeMto** es un empleado sintético capaz de calcular el trayecto entre dos estaciones de la red ATM de Barcelona (sistema integrado que permite utilizar diferentes medios de transporte: metro, autobuses, Ferrocarrils de la Generalitat (FGC), TRAMvia y Rodalies), calcular los abonos necesarios, informar sobre sus tarifas y condiciones de uso, y calcular el tiempo que tardará en llegar el siguiente metro (TMB) a una estación concreta. No se incluye el cálculo del tiempo de llegada de convoyes a las estaciones de FGC, Rodalies, TRAMvia ni de autobuses, porque está fuera del alcance del proyecto.

**ATeMto** es una ampliación de **PB-RAG-ASISTENTE-TARIFAS-ATM-BCN**, un asistente de tarifas y abonos para la red ATM de Barcelona (sistema tarifario integrado que permite utilizar diferentes medios de transporte). Ese proyecto previo no calcula rutas y solo cubre las tarifas de la ATM, no las de los medios de transporte individuales.

Por tanto, **ATeMto** utiliza el RAG construido en **PB-RAG-ASISTENTE-TARIFAS-ATM-BCN**.

**Novedades**: esta versión de **ATeMto** incorpora una API que permite a un cliente externo hacer preguntas a ATeMto y obtener sus respuestas. Para más detalle, ver la sección correspondiente.

## Estructura del proyecto

```text
PB3-ATEMTO-WITH-API/
├── .streamlit/                 # Configuración streamlit
├── api/                     
│   ├── schemas.py              # Contrato HTTP de la API.
│   ├── security.py             # Capa de seguridad de la API, para llamadas que requieren KEY.
│   ├── rate_limit.py           # Para controlar muchas llamadas seguidas y evitar ataques masivos.
│   └── app_api.py              # Entrada de la API.    
├── assets/                     
│   ├── estacions.csv           # Lista de estaciones para extraer el ID necesario para la API de TMB.
│   └── plano_ATM.jpg           # Plano para el especialista de recorridos.
├── common/                     # Carpeta donde guardamos ficheros comunes como config o utils.
│   ├── config.py               # Se definen parámetros generales del sistema.
│   ├── cargar_api_key.py       # Carga de API key de Gemini.
│   └── utils.py                # Funciones genéricas auxiliares y reutilizables.
├── data/                       # Corpus del RAG
├── database/                   # Código del modelo y persistencia de datos
│   ├── db.py                   # Persistencia del historial con SQLModel.
│   └── models.py               # Modelos SQLModel del historial.
├── entregables/                # memorias e informe final.
│   ├── memoria_agent.md        # memoria de la parte de multiagente.
│   ├── memoria_api_mlops.md    # memoria de la parte de API y MLOps.
│   └── memoria_rag.md          # memoria de la parte de rag.
├── img/                        # Imágenes varias de apoyo.
├── multiagent/                 # Carpeta donde guardamos los ficheros de la capa de negocio del multiagente.
│   ├── agent.py                # procesar_turno, aprobar_plan, run_demo
│   ├── graph.py                # StateGraph multiagente + MemorySaver + HITL
│   ├── llm.py                  # ChatGoogleGenerativeAI
│   ├── state.py                # estado de producto (UI / resumen)
│   └── tools/
│       ├── __init__.py         # allowlist (@tool) + ejecutar_tool
│       ├── api_tiempos_tmb.py  # Tool, para más detalle ver memoria.
│       ├── info_estacion.py    # Tool, para más detalle ver memoria.
│       ├── rag_tarifas.py      # Tool, para más detalle ver memoria.
│       ├── ruta_plano.py       # Tool, para más detalle ver memoria.
│       └── zonas.py            # Tool, para más detalle ver memoria.
├── output/                     # Ficheros generados entre ellos el índice de ChromaDB
├── presentaciones/             # Presentaciones comerciales del producto
│   ├── Presentacion_ATeMto.pdf # Presentación general del producto.
│   └── Presentacion_API.pdf    # Presentación de la API del producto.
├── queries/                    # Preguntas de evaluación para el RAG y resultados de las evaluaciones
│   ├── preguntas_eval.json
│   ├── preguntas_respuestas_topk1.md
│   └── preguntas_respuestas_topk5.md
├── rag/                        # Carpeta donde guardamos los ficheros de la capa de negocio del RAG.
│   ├── pipeline.py             # Orquestador de la ingesta y otras llamadas.
│   ├── load.py                 # Revisa los ficheros del corpus y lo carga con metadatos.
│   ├── chunks.py               # Construye los chunks
│   ├── embed.py                # Genera el embedding
│   ├── index.py                # Genera el índice de ChromaDB
│   ├── retriever.py            # Embedding de la consulta y recuperación de chunks
│   ├── clean.py                # Limpieza de documentos. Podría estar en utils.py
│   ├── context.py              # Formatea contexto. Podría estar en utils.py
│   ├── eval_retrieval.py       # Para la opción --eval
│   ├── prompts.py              # Construye el prompt 
│   └── generate.py             # Llama al modelo para el RAG.
├── services/                   # Carpeta donde se encuentran los servicios que llamará Streamlit u otros.
│   ├── multiagent_service.py   # Servicios que ejecutan el multiagente.
│   └── rag_service.py          # Servicios relacionados con RAG.
├── README.md
├── Dockerfile                  # Imagen Docker de la API.
├── .dockerignore
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py                     # CLI: prepare / index / query / ask.
├── app_rag.py                  # Asistente de tarifas - RAG en Streamlit.
└── app_agent.py                # Multiagente en Streamlit.


```

## Instalación del entorno de desarrollo y APIs

Obtención del código fuente via git:

```text
git clone https://github.com/rmolinao-stack/PB3-ATEMTO-WITH-API
```

Se recomienda la instalación de un entorno virtual como Conda o venv. Ejemplo:

```text
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
```

Se deben instalar los paquetes requeridos:

```text
pip install -r requirements.txt
```

Se deben crear las API KEY y el resto de variables en `.env` usando el ejemplo:

```text
cp .env.example .env
```

**Importante:** `DATABASE_URL` es obligatoria en todos los modos de ejecución (API, Streamlit y CLI): `common/config.py` lanza un error al importarse si falta.

### API Keys y variables de entorno necesarias:

* **GEMINI_API_KEY**: API key de Gemini. Necesaria tanto para el embedding del RAG como para la ejecución del asistente de tarifas y del multiagente.
* **TMB_API_ID**: Identificador de la aplicación dada de alta en developer.tmb.cat. Se usa junto con `TMB_API_KEY`. Para más información ver el apartado especial de esta API en la memoria y visitar: https://developer.tmb.cat/docs/getting-started
* **TMB_API_KEY**: API key para conectar con el servicio iMetro y conocer en tiempo real cuándo llega el siguiente tren a una estación. Se usa junto con `TMB_API_ID`. Para más información ver el apartado especial de esta API en la memoria y visitar: https://developer.tmb.cat/docs/getting-started
* **API_KEY**: Clave que deben enviar los clientes de la API de ATeMto (parámetro `api_key`) para acceder a los endpoints protegidos.
* **RATE_LIMIT_PER_MINUTE**: Máximo de peticiones por clave en 60 s.
* **CORS_ORIGINS**: Orígenes permitidos por CORS, separados por coma.
* **CORS_ALLOW_CREDENTIALS**: Permite enviar cookies y credenciales en las peticiones CORS (debe ser `false` si `CORS_ORIGINS=*`).
* **ASK_TIMEOUT_SECONDS**: Timeout por turno del agente en la API.
* **DATABASE_URL**: URL de la base de datos PostgreSQL donde se persiste el historial de la API. Obligatoria en todos los modos de ejecución.

## Modos de Ejecución ATeMto local

### Construcción de RAG y ejecución aislada

Hay dos modos de ejecución:

* Modo 1: Por línea de comandos usando python main.py y su correspondiente parámetro. Se usa principalmente para la ingesta, el embedding, la indexación y la realización de juego de pruebas del RAG.

```text
  python main.py --prepare                 #"Ingesta + embeddings (tiempo estimado de ejecución ~ 10 min)"
  python main.py --solo-ingesta            #"Solo realizar la ingesta sin ejecutar embeddings"
  python main.py --index                   #"Indexar en ChromaDB"
  python main.py --recreate-index          #"Borra la colección de ChromaDB antes de indexar"
  python main.py --query                   #"Pregunta de prueba que solo ataca al retrieval (recuperación de contexto)"
  python main.py --ask                     #"Pregunta con respuesta generada por el modelo (RAG completo)"
  python main.py --eval                    #"Evaluación con preguntas preestablecidas"
  python main.py --top-k                   #"Sobreescribe TOP-K"
  ```

* Modo 2: Desde línea de comandos usar *streamlit run app_rag.py*. Ejecuta el servidor de Streamlit y abre un chat para interactuar con el asistente.

```text
streamlit run app_rag.py
```

### Para ejecutar el multiagente en local:

Hay dos modos de ejecución:

* Modo 1: Por línea de comandos usando python main.py y su correspondiente parámetro. Se usa principalmente para ejecutar una demo completa del multiagente y para hacer una verificación interactiva del mismo solo por línea de comandos.

```text
  python main.py --agente-interactivo           # Ejecuta el workflow del multiagente por CLI en modo interactivo
  python main.py --agente-demo                  # Ejecuta una demo del workflow del multiagente por CLI. Por defecto autoaprueba las acciones.
  python main.py --agente-max-turns 4           # Limita el número máximo de turnos del workflow del multiagente
  python main.py --agente-max-steps 4           # Limita el número máximo de pasos del workflow del multiagente
  python main.py --agente-sin-auto-aprobar      # Solo para --agente-demo. Desactiva la autoaprobación de acciones.
```

* Modo 2: Desde línea de comandos usar *streamlit run app_agent.py*. Ejecuta el servidor de Streamlit y abre un chat para interactuar con el multiagente.

```text
streamlit run app_agent.py
```

### Testeo de tools multiagente en local:

```text
  python main.py --test-tool-rag-tarifas      # Ejecuta un test de pruebas para la tool rag-tarifas.
  python main.py --test-tool-plano            # Ejecuta un juego de pruebas para la tool calcular_ruta_plano.
  python main.py --test-tool-zonas            # Ejecuta un test de pruebas para la tool de obtención de la zona de varias poblaciones.
  python main.py --test-tool-id-estacion      # Ejecuta un test de pruebas para la tool de obtención del ID_ESTACION a partir del nombre de la estación.
  python main.py --test-tool-llegada-tren     # Ejecuta un test de pruebas para la tool de obtención de los tiempos de llegada de trenes en TMB.
  python main.py --test-tool-nombre-estacion  # Ejecuta un test de pruebas para la tool de obtención del nombre oficial de la estación.
```

### Para probar la API en local:

```text
uvicorn api.app_api:app --reload --port 8000
```

Una vez arrancada, la documentación interactiva está en http://127.0.0.1:8000/docs. Endpoints: `GET /health` (público), `POST /ask`, `POST /approve` y `GET /threads/{thread_id}/messages` (estos tres requieren `api_key`).

**Nota 1:** `DATABASE_URL` es obligatoria en cualquier modo de ejecución y, para que la API funcione, la BBDD PostgreSQL debe estar accesible. Para más detalle ver la memoria del proyecto.

**Nota 2:** Se recomienda el uso de Docker, para más detalle ver la memoria del proyecto. 

## Orden de ejecución estándar ATeMto local para multiagente

* Paso 1: Cargar corpus, embedding y recrear index:

```text
python main.py --prepare --index --recreate-index
```

* Paso 2: Ejecutar servidor streamlit e interactuar con el multiagente:

```text
streamlit run app_agent.py
```

## API: END-POINTS

La documentación interactiva (Swagger) está en `/docs` y `/` redirige a ella.

| Método | Ruta | Descripción | Requiere `api_key` |
|--------|------|-------------|:------------------:|
| GET | `/health` | Estado del servicio y motor de BBDD usado | No |
| POST | `/ask` | Envía una pregunta a ATeMto y devuelve su respuesta | Sí |
| POST | `/approve` | Aprueba o rechaza un plan pendiente de confirmación (HITL) | Sí |
| GET | `/threads/{thread_id}/messages` | Devuelve el historial de una conversación desde la BBDD | Sí |

Para más detalle ver la memoria de API y MLOps.

## BBDD PostgreSQL

La API requiere de una BBDD PostgreSQL para persistir las conversaciones. El detalle de cómo se puede construir en local se explica en la memoria.

## Memoria del proyecto

**Memoria de la construcción del multiagente**: [Pulsa aquí](./entregables/memoria_agent.md)
* En esta memoria podrás encontrar los detalles de arquitectura del multiagente, tales como el workflow de LangGraph que se ha implementado, la descripción de los especialistas, las tools incluidas en el proyecto y detalles sobre la API de iMetro utilizada entre otros detalles.

**Memoria de la construcción del RAG**: [Pulsa aquí](./entregables/memoria_rag.md)
* En esta memoria podrás encontrar los detalles de arquitectura específicos del RAG que se utiliza en la tool rag_tarifas y que viene heredada del proyecto PB-RAG-ASISTENTE-TARIFAS-ATM-BCN

**Memoria de la API y MLOps**: [Pulsa aquí](./entregables/memoria_api_mlops.md)
* En esta memoria podrás encontrar los detalles de los contenedores Docker (API y PostgreSQL), el gráfico del sistema desplegado, el contrato de los endpoints, los datos que se persisten, los entornos de despliegue en Render, la prueba de vida, las conclusiones de arquitectura, costes y CI/CD, y las mejoras pendientes.





