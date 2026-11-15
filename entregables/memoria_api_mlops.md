# Memoría del proyecto de MLOPS y API

En este apartado se describen los detalles relacionados con la construcción de la API y MLOPS


## Arreglos/modificaciones proyecto anterior de multiagente:

En este apartado se describen los arreglos y mejoras que se han realizado sobre el RAG para este proyecto:

* Se arreglan los errores tipográficos indicados en la evaluación del anterior proyecto. Concretamente: Nombre de la presentación, ficheros init en la estructura de carpetas, nombre incorrecto del repo.
* Se ha añadido override=True a load_dotenv para garantizar que las variables se cargar siempre. Esto viene dado porque en varios lugares se cargar variables de entorno y para garantizar que el sistema siempre carga la última se fuerza la sobreescritura. Como mejora se debería refactorizar y hacer que todo tire de config, y en cofig que fuera el único sitio donde se carguen variables de entorno, pero esto está fuera del scope actual.
* Se eliminan algunos prints de control que no tienen sentido en producción. 

## Dockers

### API

Crear imagen: docker build -t atemto-image .
Arrancar docker: docker run --rm --name atemto-container -p 8000:8000 --env-file .env atemto-image

### Postgres

Creación del docker:

docker run --name postgres-atemto -e POSTGRES_USER=EL_USUARIO -e POSTGRES_PASSWORD=EL_PASSWORD -e POSTGRES_DB=NOMBRE_DB -p 5432:5432 -d postgres

## Decisiones técnicas

TBD

## Cosas a mejorar

* **LLM Local**: Al ser una API pública corremos el riesgo de gastar muchos tokens sin control. Una solución podría ser montar el servicio con una LLM Local que no consuma tokens. Obviamente esto tiene varias peculiaridades, desde que tenemos que tener una infraestructura propia (que podría ser en la nube) y su mantenimiento, tener en cuenta una serie de costes indirectos (por ejemplo alquiler de servidor o consumo eléctrico) o que las limitaciones del LLM local seleccionado.
* **Key por consumidor (APP_KEY)**: Para mejorar el control de uso y la seguridad, se podría añadir un APP_KEY (como la de TMB) y mantenerlo en la BBDD. De tal manera que cada consumidor tendrían su APP_KEY y así podría tener un control "de quién" hace las llamadas y qué llamadas. Obviamente esto implicaría cambiar el modelo de datos de conversaciones y mensajes.
* **Para key por header vía X-API-KEY**: Para mejorar la seguridad lo ideal es NO pasar la key por parametros sino pasarlo por header.
* **Cargar variables de entorno solo en config**: Al heredar el código de proyectos anteriores, se ha detectado que varios puntos diferentes a config.py se cargan variables de entorno. Esto no es una buena praxis ya que puede provocar que ciertas varibles queden en memoria. Se debería centralizar la carga de estas variables en el config, y sustituir/refactorizar el código para que el resto de .py solo carguen parametros del sistema desde config sin usar la carga de variables de entorno. 

## Informe de resultados

TBD

### Fallos y mejoras

TBD


