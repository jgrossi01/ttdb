# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .models_harness import *
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #__PROFILE_FIELDS__

    #__PROFILE_FIELDS__END

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name        = _("UserProfile")
        verbose_name_plural = _("UserProfile")

class MDBFile(models.Model):
    
    upload_date = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='mdb_files/')  # Ruta donde se guardarán los archivos
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    created_records = models.IntegerField(default=0)
    

    def __str__(self):
        return self.name

class TestSession(models.Model):
    connector = models.CharField(max_length=50)  # Conector en prueba
    test_type = models.CharField(max_length=50)  # Tipo de prueba
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('in_progress', 'En curso'),
            ('completed', 'Terminado'),
            ('unmeasurable', 'No medible'),  
        ],
        default='pending'
    )

    
    def __str__(self):
        return f"Test {self.id} - {self.connector} ({self.test_type})"

class TestStage(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='stages')
    stage_number = models.PositiveIntegerField()
    stage_type = models.CharField(max_length=50)
    connector_dest = models.CharField(max_length=50)  # Conector que se conecta en esta etapa
    instructions = models.TextField()  # Instrucciones para el usuario
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('completed', 'Terminado'),
            ('unmeasurable', 'No medible'),  
        ],
        default='pending'
    )
    
    def __str__(self):
        return f"Stage {self.stage_number} - {self.connector_dest}"

class TestResult(models.Model):
    stage = models.ForeignKey(TestStage, on_delete=models.CASCADE, related_name='results')
    signal_id = models.IntegerField()
    signal_name = models.CharField(max_length=50)
    conector_orig = models.CharField(max_length=50)
    pin_a = models.CharField(max_length=50)
    tooltip_a = models.CharField(max_length=50, null=True, blank=True)
    conector_dest = models.CharField(max_length=50)
    pin_b = models.CharField(max_length=50)
    tooltip_b = models.CharField(max_length=50, null=True, blank=True)
    min_exp_value = models.CharField(max_length=50)
    max_exp_value = models.CharField(max_length=50)
    measured_value = models.CharField(max_length=50, null=True, blank=True)
    result = models.CharField(max_length=50, choices=[('pending', 'Pendiente'), ('pass', 'OK'), ('fail', 'NO OK')], default='pending') # OK , NO OK , PENDIENTE
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.signal_name}: {self.result}"
        
class RelayCard(models.Model):
    """Placa PXI con canales de relé."""
    name = models.CharField(max_length=50, unique=True)  # ej. "PXI-1"
    bus = models.IntegerField() # ej. "25"
    device = models.IntegerField() # ej. "8"

    def __str__(self):
        return self.name

class Adapter(models.Model):
    """
    Adaptador físico, p. ej. “Cable chasis → PXI-1”,
    que conecta varios PhysicalConnector entre sí.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class PhysicalConnector(models.Model):
    """
    Una instancia física de conector (DB15-M, DB78-H, DB50F, etc.),
    asociada a un adaptador específico.
    """
    adapter         = models.ForeignKey("Adapter", on_delete=models.CASCADE, related_name="physical_connectors")
    connector_type  = models.CharField(max_length=50)  # ej. "DB50F", "DB25M"
    label           = models.CharField(max_length=50)  # ej. "Conector A", "Conector B"

    class Meta:
        unique_together = ('adapter', 'label')

    def __str__(self):
        return f"{self.adapter.name} | {self.label}"

class AdapterConnection(models.Model):
    """
    Una relación “unidireccional” dentro de un Adapter:
      de un PhysicalConnector TEST al PhysicalConnector PXI.
    """
    adapter          = models.ForeignKey(Adapter, on_delete=models.CASCADE, related_name="connections")
    test_connector   = models.ForeignKey(PhysicalConnector, on_delete=models.PROTECT, related_name="as_test_connections")
    pxi_connector    = models.ForeignKey(PhysicalConnector, on_delete=models.PROTECT, related_name="as_pxi_connections")

    class Meta:
        unique_together = ("adapter", "test_connector", "pxi_connector")

    def __str__(self):
        return f"{self.adapter.name}: {self.test_connector.label} → {self.pxi_connector.label}"


class AdapterPinMap(models.Model):
    """
    Para cada AdapterConnection, mapea un pin del conector de TEST
    a un canal de RelayCard (PXI channel).
    """
    adapter_connection = models.ForeignKey(
        AdapterConnection,
        on_delete=models.CASCADE,
        related_name="pin_maps"
    )
    test_pin    = models.PositiveIntegerField()  # p. ej. 1..50
    relay_card  = models.ForeignKey(RelayCard, on_delete=models.CASCADE, related_name="pin_maps")
    pxi_channel = models.PositiveIntegerField()  # 1..74

    class Meta:
        unique_together = ("adapter_connection", "test_pin", "relay_card", "pxi_channel")

    def __str__(self):
        ac = self.adapter_connection
        return (
            f"{ac.adapter.name} | {ac.test_connector.label}-pin{self.test_pin} → "
            f"{ac.pxi_connector.label}-ch{self.pxi_channel}"
        )
        
class ConnectionConfig(models.Model):
    """Placa PXI con canales de relé."""
    ip_port = models.CharField(max_length=50, unique=True)  # ej. "tcp://10.245.1.103:9194"
    
    def __str__(self):
        return self.ip_port
