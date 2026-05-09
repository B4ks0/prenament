from django.contrib import admin
from .models import KaderProfil, Jadwal


@admin.register(KaderProfil)
class KaderProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'posyandu', 'wilayah', 'get_jumlah_ibu')
    list_filter = ('wilayah',)
    search_fields = ('user__nama_lengkap', 'posyandu')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Jadwal)
class JadwalAdmin(admin.ModelAdmin):
    list_display = ('kader', 'judul', 'tanggal', 'waktu')
    list_filter = ('tanggal', 'kader')
    search_fields = ('judul', 'kader__user__nama_lengkap')
    readonly_fields = ('created_at', 'updated_at')
