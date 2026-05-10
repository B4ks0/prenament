from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Pesan(models.Model):
    pengirim  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pesan_keluar')
    penerima  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pesan_masuk')
    isi       = models.TextField()
    dibaca    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Pesan'
        verbose_name_plural = 'Pesan'

    def __str__(self):
        return f'{self.pengirim.username} → {self.penerima.username}: {self.isi[:40]}'

    @classmethod
    def get_conversation(cls, user_a, user_b):
        from django.db.models import Q
        return cls.objects.filter(
            Q(pengirim=user_a, penerima=user_b) |
            Q(pengirim=user_b, penerima=user_a)
        ).order_by('created_at')

    @classmethod
    def unread_count(cls, user):
        return cls.objects.filter(penerima=user, dibaca=False).count()
