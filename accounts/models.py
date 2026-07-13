from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # We'll keep only one admin – no extra fields needed
    pass