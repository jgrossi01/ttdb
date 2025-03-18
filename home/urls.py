from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('db-manager/', views.db_manager, name='db_manager'),
    path('upload-mdb/', views.upload_mdb, name='upload_mdb'),
    path('api/databases/', views.getDatabases, name='get_databases'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)