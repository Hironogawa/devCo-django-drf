# Creating a new Django app

Django apps are the building blocks of a Django project. They are used to seperate the different parts of a project and to make it easier to maintain and extend. Such an app can be a blog, a forum or a simple guestbook. The simple rule is: If you can imagine it as a standalone application, it should be a Django app.
In this tutorial we are starting with an `account` app, which will be used to manage user accounts.

We also creat a custom user model, which is a good practices in the beginning of a project. This way we can easily extend the user model later on.

## Creating a new app

To create a new app we use the `startapp` command. This command creates a new folder with the name of the app and some files inside. Open a terminal and make sure the virtual environment is activated and that you're in the backend folder.

Make sure docker compose is running and execute the following command:

```bash
docker compose up # --build # if you want to rebuild the image or if you didn't build it yet
```

Look for the backend container Name and copy it:

```bash
docker ps
```

Open a new terminal and access the backend container:

```bash
docker exec -it <container-id> bash
```

Now you are ready to create the new app.

In the terminal (backend container) execute the following command:

```bash
python manage.py startapp accounts
```

### Registering the app

New apps need to be registrated in the `settings.py` file (backend/config/settings.py). Open the file and add the app to the `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    'accounts',
]
```

### Creating the user model

We now extend the `User` model from Django to add some additional fields. In the `accounts/models.py` file add the following code:

```python
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )  # unique is nor required and the database has to do extra work here, but it ensures that the id is unique and prevent the possibility of a collision
    email = models.EmailField(
        blank=True, unique=True, max_length=254, verbose_name="email address"
    )
    mobile_number = models.CharField(
        max_length=20, blank=True, verbose_name="mobile number"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="birth date")

    def __str__(self):
        return self.email
```

### Update the settings to use the custom user model

In the `settings.py` file add the following code, you can add it before the AUTH_PASSWORD_VALIDATORS setting:

```python
AUTH_USER_MODEL = "accounts.User" # to set the custom user model as the default user model
```

### Create the migrations

Make sure you are in the backend container and execute the following commands:

```bash
python manage.py makemigrations
```

The migrations are now created, but not applied yet. To apply the migrations execute the following command:

```bash
python manage.py migrate
```

### Add the custom user model to the admin site

In the `accounts/admin.py` file add the following code:

```python
from django.contrib import admin
from .models import User

admin.site.register(User)
```

### Create a superuser

To access the admin site we need to create a superuser. Execute the following command (in the backend container) and follow the instructions:

```bash
python manage.py createsuperuser
```

### Test the admin site

Open the browser and go to http://localhost:8000/admin. Login with the superuser account you just created. You should see the user model in the admin site.
Also check if the custom user model is visible in the admin site.

### Build a simple HTTPResponse site that shows the user data

1. Add a new view to the `accounts/views.py` file:

```python
from django.http import HttpResponse
from .models import User

def UserAccountView(request):
    user = User.objects.get(username=request.user)
    return HttpResponse(f"Hello, {user.email}")
```

2. First add the path to the app in the config urls file `backend/config/urls.py`. Here you can set the starting slug to your app, in this case we use `accounts/`, that is the starting slug for all the urls in the accounts app. You can also use an empty string `""` as the starting slug, but be aware that this could cause conflicts with other apps if your project grows, but it's up to you how you want to structure your project.

```python
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
]
```

3. Now the base slug is set and we can add the view to the accounts urls.py file `backend/accounts/urls.py`.
   Create a `urls.py` file inside the accounts folder and add the following code:

```python
from django.urls import path
from . import views

urlpatterns = [
    # base slug is accounts/
    path("", views.UserAccountView, name="user_account"), # this is the root url for the accounts app, so it's accounts/ if we leave the base slug empty
]
```

4. Now we can test the view. Open the browser and go to http://localhost:8000/accounts/. You should see the email address of the superuser.

# The end of the 2nd part of the tutorial

Good job! You created a new app with a custom user and a view.

So far, you've built the basic parts of your project. You can keep working on the frontend by using "only" the Django templates or add an API that can be consumed by a frontend framework like React or Vue, or a mobile app. You're also not limited to one or the other. You could for example start your project with Django templates and add an API later. Keep in mind that means more work. It's always a good advice to think about what your project requirements are and what you really need. If you know that you want to work with a decoupled frontend or a mobile app, it's a good idea to start directly with an API and skip the Django templates. But some projects are just fine with only Django templates. Also if you need only an API without all the features of Django, you could consider to use a microframework like Flask or FastAPI. I personally like to use Django for it's flexibility and the batteries included approach and community support.
