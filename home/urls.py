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
    path("tests/<int:session_id>/preview/", views.test_preview, name="test_preview"),
    path("tests/<int:session_id>/result/", views.test_result, name="test_result"),
    path('test-log/', views.test_log, name='test_log'),
    path('tests/<int:session_id>/stage/<int:stage_id>/', views.test_stage_view, name='test_stage'),
    path("hardware-admin/", views.hardware_admin, name="hardware_admin"),
    path("api/hardware/<str:model_name>/", views.api_get_hardware_model, name="get_hardware_model"),
    path("api/hardware/save/", views.api_save_hardware_edit, name="save_hardware_edit"),
    path("api/hardware/create/", views.api_create_hardware_record, name="create_hardware_record"),
    
    #Hardware
    path('test-hardware/', views.test_hardware, name='test_hardware'),

    
    # Funciones
    path('upload-mdb/', views.upload_mdb, name='upload_mdb'),
    
    # API
    path('api/databases/', views.getDatabases, name='get_databases'),
    path('api/harness/', views.editConexionesHarness, name='get_harness'),
    path('api/backup-harness/', views.backup_harness_ajax, name='backup_harness_ajax'),
    path('api/saveEditHarness/', views.saveConexionesHarness, name='save_edit_harness'),
    path('api/latest-db-update', views.getLastDbUpdate, name='get_last_update'),
    path("api/delete-test-session/<int:session_id>/", views.delete_test_session, name="delete_test_session"),
    path('api/run-test-stage/', views.run_test_stage, name='run_test_stage'),
    
    # Logs   
    path("events/", include(django_eventstream.urls), {"channels": ["dbupdate"]}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)