from django.contrib import admin
from .models import Notifikasi

@admin.register(Notifikasi)
class NotifikasiAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tipe', 'penerima', 'pengirim', 'dibaca', 'created_at')
    list_filter  = ('tipe', 'dibaca')
    search_fields = ('judul', 'pesan', 'penerima__username')
