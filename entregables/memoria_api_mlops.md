# Memoría del proyecto de MLOPS y API

En este apartado se describen los detalles relacionados con la construcción de la API y MLOPS


## Arreglos/modificaciones proyecto anterior de multiagente:

En este apartado se describen los arreglos y mejoras que se han realizado sobre el RAG para este proyecto:

* Se arreglan los errores tipográficos indicados en la evaluación del anterior proyecto. Concretamente: Nombre de la presentación, ficheros init en la estructura de carpetas, nombre incorrecto del repo.

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
TBD

## Informe de resultados

TBD

### Fallos y mejoras

TBD


