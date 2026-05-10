from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notifikasi(models.Model):
    TIPE_CHOICES = (
        ('reminder', 'Reminder Skrining'),
        ('pesan',    'Pesan dari Kader'),
        ('jadwal',   'Info Jadwal'),
        ('sistem',   'Sistem'),
    )

    penerima   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifikasi_masuk')
    pengirim   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifikasi_keluar')
    judul      = models.CharField(max_length=255)
    pesan      = models.TextField()
    tipe       = models.CharField(max_length=20, choices=TIPE_CHOICES, default='pesan')
    dibaca     = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notifikasi'
        verbose_name_plural = 'Notifikasi'

    def __str__(self):
        return f'[{self.tipe}] {self.judul} → {self.penerima.username}'
