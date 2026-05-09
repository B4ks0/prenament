from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ibu', 'Ibu Hamil'),
        ('kader', 'Kader Posyandu'),
        ('petugas', 'Petugas Puskesmas'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='ibu'
    )
    nama_lengkap = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
