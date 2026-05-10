from django.urls import path
from . import views

app_name = 'kader'

urlpatterns = [
    path('beranda/', views.beranda, name='beranda'),
    path('daftar-ibu/', views.daftar_ibu, name='daftar_ibu'),
    path('monitor/', views.monitor, name='monitor'),
    path('detail/<int:pk>/', views.detail_ibu, name='detail_ibu'),
    path('detail/<int:pk>/pesan/', views.kirim_pesan_ibu, name='kirim_pesan_ibu'),
    path('detail/<int:pk>/rujuk/', views.rujuk_puskesmas, name='rujuk_puskesmas'),
    path('jadwal/', views.jadwal, name='jadwal'),
    path('laporan/', views.laporan, name='laporan'),
    path('profil/', views.profil, name='profil'),
]
