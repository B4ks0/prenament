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

    def get_foto_url(self):
        try:
            if self.role == 'ibu' and self.ibu_profil.foto:
                return self.ibu_profil.foto.url
            if self.role == 'kader' and self.kader_profil.foto:
                return self.kader_profil.foto.url
            if self.role == 'petugas' and self.petugas_profil.foto:
                return self.petugas_profil.foto.url
        except Exception:
            pass
        return None
