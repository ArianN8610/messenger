from django.db import models
from django.contrib.auth.models import AbstractUser

from image_cropping import ImageRatioField


class User(AbstractUser):
    email = models.EmailField(verbose_name='email address', unique=True)
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cropping = ImageRatioField('avatar', '300x300')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()
