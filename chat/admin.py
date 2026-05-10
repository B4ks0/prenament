from django.contrib import admin
from .models import Pesan

@admin.register(Pesan)
class PesanAdmin(admin.ModelAdmin):
    list_display = ('pengirim', 'penerima', 'isi', 'dibaca', 'created_at')
    list_filter = ('dibaca',)
