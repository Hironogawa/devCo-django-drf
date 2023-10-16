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
