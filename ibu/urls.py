from django.urls import path
from . import views

app_name = 'ibu'

urlpatterns = [
    path('beranda/', views.beranda, name='beranda'),
    path('skrining/', views.skrining, name='skrining'),
    path('skrining/hasil/', views.hasil_skrining, name='hasil_skrining'),
    path('edukasi/', views.edukasi, name='edukasi'),
    path('relaksasi/', views.relaksasi, name='relaksasi'),
    path('siaga/', views.siaga, name='siaga'),
    path('profil/', views.profil, name='profil'),
]
