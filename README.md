# pandoc_api

## Introduction

The [Lab Manual Template](https://github.com/mjaquiery/lab-manual) service 
produces structured markdown documents containing lab manuals written by
users. 
This repository acts as a listener to allow the service to convert the markdown
into formats more useful for dissemination -- primarily HTML, PDF, and DOCX.

## Project structure

### Django

The project is written in Python, using Django and the Django REST Framework.
The main Django project is `web/pandoc_api`, which holds the settings etc.
The only Django app is `web/rest`. 

### Docker-compose

The project is wrapped in a docker-compose environment to tie its resources 
together.
There is a database (**db**) running Postgresql to store the project data.
Redis (**redis**) acts as an information broker between the webserver (**web**)
and the Celery backend (**worker**). 
The webserver's job is to provide the REST framework, and the Celery backend
processes document conversion jobs as they are submitted to the REST framework.

## Using the REST API

The API exposes the following endpoints:

### `GET /jobs/`

Sending a GET request to /jobs/ returns a JSON file listing all the jobs in the database.
Jobs that have been completed will have an _output_ property, containing a relative link 
to the file.

### `POST /jobs/`

POST requests may be sent to /jobs/ with the following JSON information:

```json5
{
  "document": "# Markdown\n\nSome text.", 
  "format": "html"
}
```

_Document_ contains the markdown to be converted in string format. 
_Format_ contains the target format. 
It must be one of those listed in `GET /formats/`.

A JSON response will be returned containing the job information.
Note down the job id because this will be useful later for tracking
the progress on the job.

### `GET /formats/`

The supported formats are returned as a JSON list in response to GET requests to /formats/.

### Workflow

Requests are submitted to the REST API through `POST /jobs/`. 
Received requests will be queued for conversion. 
The status of the conversion can be monitored via `GET /jobs/` requests.
When an output appears in the relevant job in the response to `GET /jobs/`, 
visit the link shown in the output to download the converted file.

## Development

Docker-compose makes development fairly easy.
To get things up and running, the only additional files you should need are the 
environment files.
There are two you will need to make, `.env.django` and `.env.postgres`.

The keys required and the kinds of values required are:

### `.env.django`

```dotenv
DJANGO_SECRET_KEY= # Some secret key used by Django. Should be long and complex.
DJANGO_ALLOWED_HOSTS= # space-separated list of allowed hosts for Django. Can be * for development.
DJANGO_LOG_LEVEL=  # One of DEBUG, INFO, WARNING, ERROR, NONE (other log levels are not implemented)
DJANGO_DEBUG=  # Whether to run Django in Debug Mode
```

### `.env.postgres`

```dotenv
POSTGRES_DB=  # database name, postgres is fine
POSTGRES_USER=  # database user's name. Again, postgres is fine
POSTGRES_PASSWORD=  # database password. Whatever you like (again, postgres is fine!)
```

The environment files reduce repetition when binding Django and Postgres, and avoid having
to commit sensitive Django stuff to the repository.
With those files in place, the project should be runnable as simply as 

```shell
docker-compose up --build
```
