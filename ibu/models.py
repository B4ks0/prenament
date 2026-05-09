from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class ArtikelEdukasi(models.Model):
    KATEGORI_CHOICES = (
        ('kecemasan', 'Kecemasan'),
        ('depresi', 'Depresi'),
        ('nutrisi', 'Nutrisi'),
        ('persalinan', 'Persiapan Persalinan'),
        ('bayi', 'Perawatan Bayi'),
        ('umum', 'Umum'),
    )
    judul = models.CharField(max_length=255)
    ringkasan = models.TextField(blank=True)
    konten = models.TextField()
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='umum')
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='artikel_edukasi')
    diterbitkan = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artikel Edukasi"
        verbose_name_plural = "Artikel Edukasi"
        ordering = ['-created_at']

    def __str__(self):
        return self.judul


class IbuProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ibu_profil')
    usia = models.IntegerField(null=True, blank=True)
    alamat = models.TextField(blank=True)
    usia_kehamilan = models.IntegerField(null=True, blank=True, help_text="Dalam minggu")
    paritas = models.IntegerField(null=True, blank=True, help_text="Jumlah anak")
    kader = models.ForeignKey('kader.KaderProfil', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Ibu Hamil"
        verbose_name_plural = "Profil Ibu Hamil"
    
    def __str__(self):
        return f"Profil {self.user.nama_lengkap}"
    
    def get_skor_terakhir(self):
        try:
            return self.skrining_hasil.latest('created_at').skor
        except SkriningHasil.DoesNotExist:
            return 0
    
    def get_kategori_risiko(self):
        skor = self.get_skor_terakhir()
        if skor >= 30:
            return 'Risiko Tinggi'
        elif skor >= 15:
            return 'Risiko Sedang'
        else:
            return 'Risiko Rendah'


class SkriningHasil(models.Model):
    KATEGORI_CHOICES = (
        ('rendah', 'Risiko Rendah'),
        ('sedang', 'Risiko Sedang'),
        ('tinggi', 'Risiko Tinggi'),
    )
    
    ibu = models.ForeignKey(IbuProfil, on_delete=models.CASCADE, related_name='skrining_hasil')
    skor = models.IntegerField()
    kategori_risiko = models.CharField(max_length=10, choices=KATEGORI_CHOICES)
    jawaban = models.JSONField(default=dict)  # Simpan jawaban PRAQ-R2
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hasil Skrining"
        verbose_name_plural = "Hasil Skrining"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Skrining {self.ibu.user.nama_lengkap} - Skor {self.skor}"


class SiagaChecklist(models.Model):
    ibu = models.ForeignKey(IbuProfil, on_delete=models.CASCADE, related_name='siaga_checklist')
    nomor_item = models.IntegerField()
    sudah_dicentang = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    CHECKLIST_ITEMS = [
        (1, 'Membuat rencana persalinan'),
        (2, 'Memilih tempat persalinan'),
        (3, 'Memilih penolong persalinan'),
        (4, 'Menyiapkan biaya persalinan'),
        (5, 'Menyiapkan transportasi'),
    ]
    
    class Meta:
        unique_together = ('ibu', 'nomor_item')
        verbose_name = "Siaga Checklist"
        verbose_name_plural = "Siaga Checklist"
    
    def __str__(self):
        return f"Siaga {self.ibu.user.nama_lengkap} - Item {self.nomor_item}"
    
    def get_nomor_item_display(self):
        item_dict = dict(self.CHECKLIST_ITEMS)
        return item_dict.get(self.nomor_item, f'Item {self.nomor_item}')
