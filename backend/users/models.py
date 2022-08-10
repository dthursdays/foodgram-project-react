from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )

    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username
