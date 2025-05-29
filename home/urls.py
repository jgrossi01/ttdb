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
    path("hardware/", views.hardware, name="hardware"),
    path("hardware/new-adapter", views.new_adapter_view, name="new_adapter_view"),
    path("hardware/adapter/<int:id>/connectors", views.adapter_connectors_view, name="adapter_connectors_view"),
    path("hardware/adapter/<int:id>/connections", views.adapter_connections_view, name="adapter_connections_view"),

    
    #pruebas de conexion con pxi
    #path('test-hardware/', views.test_hardware, name='test_hardware'),

    
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
    path("api/hardware/connector-types/", views.api_connector_types, name="connector_types"),
    
    # Especificas
    path("api/hardware/connection_config/", views.api_get_connection_config, name="get_connection_config"),
    path("api/hardware/adapterconnector/create/", views.api_create_adapterconnector),
    path("api/hardware/adapterconnectors/", views.api_list_adapterconnectors),
    #path("api/hardware/check-connector-label/", views.api_check_connector_label, name="check_connector_label"),
    path("api/hardware/get-adapters/", views.api_get_adapters, name="get_adapters"),
    path("api/hardware/get-relaycards/", views.api_get_relaycards, name="get_relaycards"),
    path('api/hardware/create-adapter/', views.api_create_adapter, name='create_adapter'),
    #path('api/hardware/get-subunit-choices/', views.api_get_sub_unit_choices, name='get_subunit_choices'),
    
    # Pinmap
    path("api/hardware/adapterpinmap/", views.api_list_adapterpinmap),
    path("api/hardware/adapterpinmap/save/", views.api_save_adapterpinmap),
    path('api/hardware/adapterpinmap/bulk-update/', views.adapterpinmap_bulk_update, name='adapterpinmap_bulk_update'),
    
    # Genericas
    path("api/hardware/save/", views.api_save_hardware_edit, name="save_hardware_edit"),
    path("api/hardware/create/", views.api_create_hardware_record, name="create_hardware_record"),
    path("api/hardware/delete/", views.api_delete_hardware_record, name="delete_hardware_record"),
    #path("api/hardware/<str:model_name>/", views.api_get_hardware_model, name="get_hardware_model"), #Mantener abajo para evitar errores

    
    # Logs   
    path("events/", include(django_eventstream.urls), {"channels": ["dbupdate"]}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)