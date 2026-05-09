"""
URL configuration for prenament project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth URLs
    path('', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    
    # App URLs
    path('ibu/', include('ibu.urls', namespace='ibu')),
    path('kader/', include('kader.urls', namespace='kader')),
    path('petugas/', include('petugas.urls', namespace='petugas')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
