# Django Rest Framework

We could build the entire API from scratch with Django, but we will use the Django Rest Framework (DRF) to speed up the process. DRF is provides a set of tools to rapidly build APIs for Django.

Docs: https://www.django-rest-framework.org/

## Install Django Rest Framework

1. I like to seperate the authentication app from the rest of the apps, we create a new app called `auth`:

```python
python manage.py startapp auth
```

2. Add the new app to the `config/settings.py` INSTALLED_APPS list:

```python
INSTALLED_APPS = [
    ...
    'auth',
]
```

1. Install DRF into the backend container. Make sure you are in the backend container bash and execute the following command:

```bash
pip install djangorestframework
```

2. Add the framework to the `INSTALLED_APPS` in the `backend/config/settings.py` file:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

3. If you want to use the browsable API view, add the login/logout views to the `backend/config/urls.py` file:

```python
from django.contrib import admin
from django.urls import path, include

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # <-- Add this
]
```
