from django.contrib import admin
from .models import PetugasProfil


@admin.register(PetugasProfil)
class PetugasProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nip', 'puskesmas', 'jabatan')
    search_fields = ('user__nama_lengkap', 'nip', 'puskesmas')
    readonly_fields = ('created_at', 'updated_at')
