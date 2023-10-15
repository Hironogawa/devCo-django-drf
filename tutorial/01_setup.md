# Django Docker Compose Setup

In this step we'll setup our Django project with to run in Docker containers. We'll use Docker Compose to orchestrate the containers. This setup helps us to have a local development environment that is as close as possible to the production environment. Also we don't have to install any depencecies like a database on our local machine. We can also easily extend our setup later with other containers like a Redis cache for example.

## Requirements

- LTS version of Docker (https://docs.docker.com/install/)
- Docker Compose is included with Docker for Mac and Windows. If you are using the CLI version of docker on Linux, you will need to install Docker Compose separately (https://docs.docker.com/compose/install/). There is now also a Docker Desktop version for Linux, which includes Docker Compose.
- LTS version of Python (Don't worry about installing Python on your machine, we will use Docker to run our application, but it is good to have a local version of Python installed on your machine for development purposes)

## Setup

Use the provided example.gitignore file to create a .gitignore file in your project directory. This will prevent you from committing unnecessary files to your repository. You can also use the gitignore.io website to generate a .gitignore file for your project. Basically rename the file to .gitignore.

1. With python installed, create a new virtual environment for your project. You can use the following command to create a new virtual environment in your project directory:

```bash
python -m venv venv
```

2. Activate your virtual environment:

```bash
source venv/bin/activate
```

3. Install Django:

```bash
pip install django
```

4. Create a new Django project:

```bash
django-admin startproject config
```

5. Rename the main project directory to backend:

```bash
mv config backend
```

## Add Docker to the project and configure the development environment

1. Create a new dockerfile in the application root directory (backend) and add the following:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTEsrc 1
ENV PYTHONUNBUFFERED 1

ENV APP_DIR=/var/www/app/backend

# Set the working directory to /src
WORKDIR $APP_DIR

# Install dependencies
# Copy the current directory contents into the container at /src
COPY --chown=appuser . $APP_DIR

# COPY requirements.txt /var/www/app/backend/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# to have access to the container in th the local network (docker compose) we neet to listen to any ip address 0.0.0.0
ENTRYPOINT ["python3"] # this defines the default command to run when starting the container
CMD ["manage.py", "runserver", "0.0.0.0:8000"] # this is the default command to run when starting the container for development
```

2. Create a new docker-compose.yml file in the project root directory and add the following:

```yml
version: "3.8"
# author: "Hironogawa"
# description: "This is a starter template for a django project."

services:
  postgres_db:
    image: postgres:15
    restart: always
    env_file:
      - ./backend/.env
    # environment:
    #   POSTGRES_DB: "postgres_db"
    #   POSTGRES_USER: "postgres_user"
    #   POSTGRES_PASSWORD: "postgres_password"
    ports:
      - "5432:5432"
    volumes:
      - postgres_db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backnet
  backend:
    build: ./backend
    entrypoint: ["/bin/bash", "-c"]
    # only automatically migrate and collect static files on startup and use runserver also only for local development
    command: >
      "python manage.py migrate &&
      python manage.py collectstatic --noinput &&
      python manage.py runserver 0.0.0.0:8000 --nostatic"
    # the --nostatic flag is used to prevent the default serving of static files by runserver, we use whitenoise for that
    volumes:
      - ./backend/:/var/www/app/backend/
      - static_volumes:/var/www/app/backend/staticfiles/
      - media_volumes:/var/www/app/backend/mediafiles/
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      postgres_db:
        condition: service_healthy
    # environment:
    #   POSTGRES_HOST: "postgres_db"
    #   POSTGRES_DB: "postgres_db"
    #   POSTGRES_USER: "postgres_user"
    #   POSTGRES_PASSWORD: "postgres_password"
    networks:
      - backnet
      - nginxnet
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./setup/nginx/dev-nginx.conf:/etc/nginx/nginx.conf
      - static_volumes:/var/www/app/backend/staticfiles/
      - media_volumes:/var/www/app/backend/mediafiles/
    depends_on:
      - backend
    networks:
      - nginxnet
networks:
  backnet:
    driver: bridge
  frontnet:
    driver: bridge
  nginxnet:
    driver: bridge

volumes:
  postgres_db:
    driver: local
  static_volumes:
    driver: local
  media_volumes:
    driver: local
```

3. Create a new directory called setup in the project root directory and add a new directory called nginx inside the setup directory. Add a new file called dev-nginx.conf inside the nginx directory and add the following:

```nginx
worker_processes 1;

events { worker_connections 1024; }

http {

    upstream backend_network {
        server backend:8000; # backend is the name of the container defined in the docker compose file
    }

    server {
        listen 80;
        server_name localhost;

        location /media {
            alias /var/www/app/backend/mediafiles/;
        }

        location / {
            proxy_pass http://backend_network;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

    }
}
```

3. Add a gitignore file. Use the provided example.gitignore file and rename it to .gitignore.

4. Add a .env file to the backend directory and add the following and replace the values with your own, but don't commit this file to your repository (add it to the .gitignore file):

```bash
DEBUG=True
SECRET_KEY=''
# DATABASE
POSTGRES_HOST=postgres_db
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
POSTGRES_PORT=5432
```

Now your project directory should look like this:

```
├── backend
│   ├── config
│   ├── .env
│   ├── dockerfile
│   ├── manage.py
├── setup
│   ├── nginx
│   │   ├── nginx.conf
venv
.gitignore
docker-compose.yml
README.md
```

# Django Configuration

## Add django-environ to the project

We want to work with environment variables to configure our application. We will use the django-environ package to do that. We will also use it to configure our database settings.

```bash
pip install django-environ
```

Update the settings.py file in the backend/config directory and add the following:

On the top of the file change/add the following:

```python

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# set the base path of the env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# django-environ settings to read .env file the you can use it with env("")
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

if DEBUG is True:
    # CSRF not needed because we are using JWT
    CORS_ORIGIN_ALLOW_ALL = True
    # Ref: https://osirusdjodji.medium.com/handling-cors-in-django-rest-framework-a-comprehensive-guide-ec11b0bc6807

else:
    ALLOWED_HOSTS = [env("ALLOWED_HOSTS")]

    CORS_ORGIN_WHITELIST = [
        env("CORS_ORGIN_WHITELIST"),
    ]
```

## Secret Key

The secret key is really important for the security of your application. You should never commit it to your repository. We can use the django-environ package to read the secret key from the .env file. To create a new secret key we can use the command provided by django.

1. Make sure your virtual environment is activated and run the following command, in your project root directory run the following command in your terminal:

```bash
source venv/bin/activate
```

2. CD to your backend directory and run the following command:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

3. Copy the secret key output and paste it in your .env file:

```
SECRET_KEY='your-secret-key'
```

## Database

### Database settings

To configure the database we will use the django-environ package again. Also if we are working with postgres we need to install the psycopg packege. (psycopg2 will be deprecated in the future, that's why we'll use v3 that is in the psycopg package)

```bash
pip install psycopg
```

Open the settings.py file and look for the DATABASES configuration. Replace it with the following:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env(
            "POSTGRES_DB"
        ),  # with docker compose up, we need to use the name of the service
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}
```

## Media and Static Files

### static and media file settings

We need to update the settings.py file to serve static and media files from the backend container. Add the following to the bottom of the settings.py file:

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# url which will be used to access the static files from the browser
STATIC_URL = "/static/"

# the name of the folders where the static files are stored (only if you are not using whitenoise or the django template engine)
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "static"), # add this only if you are working with the django template engine
]
# Path where the static files are collected and stored
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# url which will be used to access the media files from the browser
MEDIA_URL = "/media/"
# Path where the media is stored
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
```

We could configure our application to server static files with NGINX, but we will use whitenoise to serve the static files to keep things simple for the docekr compose setup. Also we can use it to serve the static files in production. With whitenoise we can also strap a CDN to serve the static files instead of serving them from the backend container.

We use whitenoise to serve static files in production.
Docs: https://whitenoise.readthedocs.io/en/latest/

### Installing whitenoise

```bash
pip install whitenoise
```

### Adding whitenoise to the middleware

Add the following to the bottom of the MIDDLEWARE list in the settings.py file:

```python
MIDDLEWARE = [
    ...
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
```

### Adding compression and caching support:

On Django 4.2, for older verions check the whitenoise documentation.

Add the following to the bottom of the settings.py file, below the STATIC configuration:

```python
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

## Now we need to save our installed packages to a requirements.txt file

Make sure your virtual environment is activated. CD into your backend directory and run the following command:

```bash
pip freeze > requirements.txt
```

## END OF PART 1

Your project directory should look like this:

```
├── backend
│   ├── config
│   ├── .env
│   ├── dockerfile
│   ├── manage.py
│   ├── requirements.txt
├── setup
│   ├── nginx
│   │   ├── nginx.conf
venv
.gitignore
docker-compose.yml
README.md
```

## Try if everything works

Go to your project root directory and run the following command:

```bash
docker compose up --build
```

Not check the logs and see if everything works as expected. Open your browser and go to http://localhost:8000/ and you should see the django welcome page.

### Docker Compose Problems

If you can't start docker try to run this command, to remove all containers:

```bash
docker compose down
```

If you have problems with volumes/database try to run this command, but be careful, this will remove all volumes and data:

```bash
docker compose down --volumes
```

You can also remove only a specific volume:

```bash
docker volume rm <volume-name>
```

## Running the application

```bash
docker compose up --build
```

### Accessing the container shell

Find the container id:

```bash
docker ps
```

Access the container shell:

```bash
docker exec -it <container-id> bash
```
