from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class AdminUser(AbstractUser):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        Group,
        related_name='admin_app_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='admin_app_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    REQUIRED_FIELDS = []
    