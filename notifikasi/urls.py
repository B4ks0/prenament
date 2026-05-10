from django.urls import path
from . import views

app_name = 'notifikasi'

urlpatterns = [
    path('ibu/',   views.ibu_list,    name='ibu_list'),
    path('kader/', views.kader_kirim, name='kader_kirim'),
]
