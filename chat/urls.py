from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('kader/',               views.kader_list, name='kader_list'),
    path('kader/<int:ibu_pk>/',  views.kader_room, name='kader_room'),
    path('ibu/',                 views.ibu_room,   name='ibu_room'),
    path('poll/<int:partner_pk>/', views.poll_messages, name='poll'),
]
