from django.db import models
from .managers import UserManager
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower
from .validators import username_validator


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=15,unique=True,validators=[username_validator])
    photo = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.CharField(blank=True, max_length=150)
    birth_date = models.DateField(blank=True,null=True)
    is_private = models.BooleanField(default=True)
    updated_at = models.DateTimeField( auto_now=True)
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('email'), name='user_email_ci_unique'),
            models.UniqueConstraint(Lower('username'), name='user_username_ci_unique'),
        ]

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        
        if self.email:
            self.email = self.email.strip().lower()
            
        super().save(*args, **kwargs)
        