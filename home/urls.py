from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
import django_eventstream

urlpatterns = [
    # Paginas
    path('', views.index, name='index'),
    path('db-manager/edit', views.edit_db, name='edit_db'),
    path('db-manager/update', views.update_db, name='update_db'),
    path('new-test', views.new_test, name='new_test'),
    
    # Funciones
    path('upload-mdb/', views.upload_mdb, name='upload_mdb'),
    
    # API
    path('api/databases/', views.getDatabases, name='get_databases'),
    path('api/harness/', views.editConexionesHarness, name='get_harness'),
    path('api/backup-harness/', views.backup_harness_ajax, name='backup_harness_ajax'),
    path('api/saveEditHarness/', views.saveConexionesHarness, name='save_edit_harness'),
    path('api/latest-db-update', views.getLastDbUpdate, name='get_last_update'),
    
    # Logs   
    path("events/", include(django_eventstream.urls), {"channels": ["dbupdate"]}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)