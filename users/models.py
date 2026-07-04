from django.db import models
from .managers import UserManager
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower
from django.core.validators import RegexValidator

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    objects = UserManager()
    username = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^[a-zA-Z0-9_]{3,15}$', 'Username invalido')],
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('email'), name='user_email_ci_unique'),
            models.UniqueConstraint(Lower('username'), name='user_username_ci_unique'),
        ]

    def __str__(self):
        return self.email