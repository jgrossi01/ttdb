# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .models_harness import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
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
    
    
class ConnectionConfig(models.Model):
    """Placa PXI con canales de relé."""
    ip_port = models.CharField(max_length=50, unique=True)  # ej. "tcp://10.245.1.103:9194"
    
    def __str__(self):
        return self.ip_port

        
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
    CONNECTOR_SIDE_CHOICES = [
        ('pxi-side', 'Lado PXI'),
        ('test-side', 'Lado test'),
    ]

    adapter = models.ForeignKey(
        "Adapter",
        on_delete=models.CASCADE,
        related_name="physical_connectors"
    )
    connector_type = models.CharField(max_length=50)  # Ej: "DB50F", "DB25M"
    label = models.CharField(max_length=50)  # Ej: "Conector A", "Conector B"
    pin_qty = models.PositiveIntegerField()  # Cantidad de pines del conector
    connector_side = models.CharField(
        max_length=50,
        choices=CONNECTOR_SIDE_CHOICES,
        default='test-side'
    )

    class Meta:
        unique_together = ('adapter', 'label')
        ordering = ['adapter', 'label']

    def __str__(self):
        return f"{self.adapter.name} | {self.label} ({self.get_connector_side_display()})"


class AdapterPinMap(models.Model):
    adapter = models.ForeignKey(
        "Adapter",
        on_delete=models.CASCADE,
        related_name="pin_maps",
        null=True, blank=True
    )
    pxi_connector = models.ForeignKey(
        "PhysicalConnector",
        on_delete=models.CASCADE,
        related_name="pin_maps_pxi",
        null=True, blank=True
    )
    to_pxi_pin = models.PositiveIntegerField(
        null=True, blank=True
    )
    pxi_channel = models.PositiveIntegerField(
        null=True, blank=True
    )
    pxi_channel_type = models.CharField(
        max_length=50,
        choices=[('U', 'Input'), ('M', 'Output'), ('undefined', 'No definido')],
        default='undefined',
        null=True, blank=True
    )
    relay_card = models.ForeignKey(
        "RelayCard",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="pin_maps_relay"
    )
    test_connector = models.ForeignKey(
        "PhysicalConnector",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="pin_maps_test"
    )
    to_test_pin = models.PositiveIntegerField(
        null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["adapter", "pxi_connector", "pxi_channel"],
                name="unique_pxi_mapping_per_adapter"
            )
        ]
        ordering = ['adapter', 'pxi_connector', 'pxi_channel']

    def __str__(self):
        base = f"{self.adapter.name} | {self.pxi_connector.label}"
        if self.test_connector and self.to_test_pin:
            return f"{base} → {self.test_connector.label}-pin{self.to_test_pin}"
        return f"{base} → (sin asignar)"

    def clean(self):
        # Validar que to_test_pin no supere la cantidad de pines del test_connector
        if self.test_connector and self.to_test_pin:
            if self.to_test_pin > self.test_connector.pin_qty:
                raise ValidationError({
                    'to_test_pin': f"El pin {self.to_test_pin} excede la cantidad de pines del conector {self.test_connector.label} (máximo: {self.test_connector.pin_qty})."
                })

            # Validar que no se repita el to_test_pin en el mismo test_connector y adapter
            query = AdapterPinMap.objects.filter(
                adapter=self.adapter,
                test_connector=self.test_connector,
                to_test_pin=self.to_test_pin,
            )
            if self.pk:
                query = query.exclude(pk=self.pk)
            if query.exists():
                raise ValidationError({
                    'to_test_pin': f"El pin {self.to_test_pin} ya está asignado en el conector {self.test_connector.label}."
                })

        # Validar que pxi_channel no se repita con el mismo pxi_connector y relay_card
        if self.pxi_connector and self.pxi_channel and self.relay_card:
            query = AdapterPinMap.objects.filter(
                adapter=self.adapter,
                pxi_connector=self.pxi_connector,
                pxi_channel=self.pxi_channel,
                relay_card=self.relay_card
            )
            if self.pk:
                query = query.exclude(pk=self.pk)
            if query.exists():
                raise ValidationError({
                    'pxi_channel': f"El canal PXI {self.pxi_channel} ya está asignado para este conector y relay card."
                })

                

        
        
