from django.urls import path
from . import views

app_name = 'petugas'

urlpatterns = [
    path('beranda/', views.beranda, name='beranda'),
    path('pengguna/', views.pengguna, name='pengguna'),
    path('statistik/', views.statistik, name='statistik'),
    path('profil/', views.profil, name='profil'),
    path('artikel/', views.artikel_list, name='artikel_list'),
    path('artikel/buat/', views.artikel_create, name='artikel_create'),
    path('artikel/<int:pk>/edit/', views.artikel_edit, name='artikel_edit'),
    path('artikel/<int:pk>/hapus/', views.artikel_delete, name='artikel_delete'),
]
