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
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')
    
    def __str__(self):
        return f"Test {self.id} - {self.connector} ({self.test_type})"

class TestStage(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='stages')
    stage_number = models.PositiveIntegerField()
    connector_destination = models.CharField(max_length=50)  # Conector que se conecta en esta etapa
    instructions = models.TextField()  # Instrucciones para el usuario
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    
    def __str__(self):
        return f"Stage {self.stage_number} - {self.connector_destination}"

class TestResult(models.Model):
    stage = models.ForeignKey(TestStage, on_delete=models.CASCADE, related_name='measurements')
    signal_name = models.CharField(max_length=50)
    pin_origin = models.IntegerField()
    pin_destination = models.IntegerField()
    result = models.FloatField(null=True, blank=True)  # Resultado de la medición
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.signal_name}: {self.result}"