from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class KaderProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kader_profil')
    foto = models.ImageField(upload_to='profil/', blank=True, null=True)
    posyandu = models.CharField(max_length=255, blank=True)
    wilayah = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Kader Posyandu"
        verbose_name_plural = "Profil Kader Posyandu"
    
    def __str__(self):
        return f"Kader {self.user.nama_lengkap} - {self.posyandu}"
    
    def get_jumlah_ibu(self):
        from ibu.models import IbuProfil
        return IbuProfil.objects.filter(kader=self).count()
    
    def get_ibu_risiko_tinggi(self):
        from ibu.models import IbuProfil
        return IbuProfil.objects.filter(
            kader=self,
            skrining_hasil__kategori_risiko='tinggi'
        ).distinct().count()


class Jadwal(models.Model):
    kader = models.ForeignKey(KaderProfil, on_delete=models.CASCADE, related_name='jadwal')
    judul = models.CharField(max_length=255)
    venue = models.CharField(max_length=255, blank=True)
    tanggal = models.DateField()
    waktu = models.TimeField()
    deskripsi = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Jadwal Kader"
        verbose_name_plural = "Jadwal Kader"
        ordering = ['tanggal', 'waktu']
    
    def __str__(self):
        return f"{self.judul} - {self.tanggal}"
