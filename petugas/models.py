from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PetugasProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='petugas_profil')
    foto = models.ImageField(upload_to='profil/', blank=True, null=True)
    nip = models.CharField(max_length=50, unique=True, blank=True)
    puskesmas = models.CharField(max_length=255, blank=True)
    jabatan = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Petugas Puskesmas"
        verbose_name_plural = "Profil Petugas Puskesmas"
    
    def __str__(self):
        return f"{self.user.nama_lengkap} ({self.jabatan})"
