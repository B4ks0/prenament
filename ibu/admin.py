from django.contrib import admin
from .models import IbuProfil, SkriningHasil, SiagaChecklist


@admin.register(IbuProfil)
class IbuProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'usia', 'usia_kehamilan', 'get_kategori_risiko')
    list_filter = ('created_at',)
    search_fields = ('user__nama_lengkap', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SkriningHasil)
class SkriningHasilAdmin(admin.ModelAdmin):
    list_display = ('ibu', 'skor', 'kategori_risiko', 'created_at')
    list_filter = ('kategori_risiko', 'created_at')
    search_fields = ('ibu__user__nama_lengkap',)
    readonly_fields = ('created_at',)


@admin.register(SiagaChecklist)
class SiagaChecklistAdmin(admin.ModelAdmin):
    list_display = ('ibu', 'nomor_item', 'sudah_dicentang')
    list_filter = ('sudah_dicentang',)
    search_fields = ('ibu__user__nama_lengkap',)
