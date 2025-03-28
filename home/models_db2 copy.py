# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Conectores(models.Model):
    idconector = models.IntegerField(db_column='IDConector', blank=True, null=True)  # Field name made lowercase.
    conector = models.TextField(db_column='Conector', blank=True, null=True)  # Field name made lowercase.
    link = models.TextField(db_column='Link', blank=True, null=True)  # Field name made lowercase.
    codigovuelo = models.TextField(db_column='CodigoVuelo', blank=True, null=True)  # Field name made lowercase.
    codigoingenieria = models.TextField(db_column='CodigoIngenieria', blank=True, null=True)  # Field name made lowercase.
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)  # Field name made lowercase.
    link_file = models.TextField(db_column='link_file', blank=True, null=True)
    listadepines = models.TextField(db_column='ListadePines', blank=True, null=True)  # Field name made lowercase.
    codigopinvuelo = models.TextField(db_column='CodigoPinVuelo', blank=True, null=True)  # Field name made lowercase.
    codigopiningenieria = models.TextField(db_column='CodigoPinIngenieria', blank=True, null=True)  # Field name made lowercase.
    datasheet = models.TextField(db_column='datasheet', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Conectores'


class Conexiones(models.Model):
    field_de_señal = models.FloatField(db_column='# de Señal', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it started with '_'.
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)  # Field name made lowercase.
    tipo_señal = models.TextField(db_column='Tipo Señal', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.TextField(db_column='Descripción', blank=True, null=True)  # Field name made lowercase.
    señal_unidad = models.TextField(db_column='Señal Unidad', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sistema = models.TextField(db_column='Sistema', blank=True, null=True)  # Field name made lowercase.
    subsistema = models.TextField(db_column='Subsistema', blank=True, null=True)  # Field name made lowercase.
    unidad = models.TextField(db_column='Unidad', blank=True, null=True)  # Field name made lowercase.
    modulo = models.TextField(db_column='Modulo', blank=True, null=True)  # Field name made lowercase.
    in_out = models.TextField(db_column='IN/OUT', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    origen = models.TextField(db_column='Origen', blank=True, null=True)  # Field name made lowercase.
    conector_orig = models.TextField(db_column='Conector Orig', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pin_orig = models.TextField(db_column='Pin Orig', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tipo_de_con_orig = models.TextField(db_column='Tipo de Con Orig', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    awg = models.TextField(db_column='AWG', blank=True, null=True)  # Field name made lowercase.
    longitud = models.TextField(db_column='Longitud', blank=True, null=True)  # Field name made lowercase.
    manguera = models.TextField(db_column='Manguera', blank=True, null=True)  # Field name made lowercase.
    shield = models.TextField(db_column='Shield', blank=True, null=True)  # Field name made lowercase.
    twisted = models.TextField(db_column='Twisted', blank=True, null=True)  # Field name made lowercase.
    señal_unidad1 = models.TextField(db_column='Señal Unidad1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sistema1 = models.TextField(db_column='Sistema1', blank=True, null=True)  # Field name made lowercase.
    subsistema1 = models.TextField(db_column='Subsistema1', blank=True, null=True)  # Field name made lowercase.
    unidad1 = models.TextField(db_column='Unidad1', blank=True, null=True)  # Field name made lowercase.
    modulo1 = models.TextField(db_column='Modulo1', blank=True, null=True)  # Field name made lowercase.
    in_out1 = models.TextField(db_column='IN/OUT1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    destino = models.TextField(db_column='Destino', blank=True, null=True)  # Field name made lowercase.
    conector_dest = models.TextField(db_column='Conector Dest', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pin_dest = models.TextField(db_column='Pin Dest', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tipo_de_con_dest = models.TextField(db_column='Tipo de Con Dest', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    obsev = models.TextField(db_column='Obsev', blank=True, null=True)  # Field name made lowercase.
    interface = models.TextField(db_column='Interface', blank=True, null=True)  # Field name made lowercase.
    frec = models.TextField(db_column='Frec', blank=True, null=True)  # Field name made lowercase.
    imax = models.TextField(db_column='Imax', blank=True, null=True)  # Field name made lowercase.
    drop_voltage = models.TextField(db_column='Drop Voltage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    clase_emi_emc = models.TextField(db_column='Clase EMI/EMC', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    clase_repuesto_field = models.TextField(db_column='Clase(Repuesto)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    integrada_si_no_field = models.TextField(db_column='Integrada(si/no)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    documento = models.TextField(db_column='Documento', blank=True, null=True)  # Field name made lowercase.
    activo_si_no_field = models.TextField(db_column='activo(si/no)', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    observacion_activo_si_no_field = models.TextField(db_column='Observacion(activo si/no)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    PEM_Polaridad = models.TextField(db_column='PEM_Polaridad', blank=True, null=True)
    PEM_Telemetria = models.TextField(db_column='PEM_Telemetria', blank=True, null=True) 
    PEM_tipo_señal = models.TextField(db_column='PEM_tipo_señal', blank=True, null=True)   

    class Meta:
        managed = False
        db_table = 'Conexiones'


class Tipocable(models.Model):
    idcable = models.IntegerField(db_column='IDCable', blank=True, null=True)  # Field name made lowercase.
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)  # Field name made lowercase.
    nombrecable = models.TextField(db_column='NombreCable', blank=True, null=True)  # Field name made lowercase.
    nombrealambre = models.TextField(db_column='NombreAlambre', blank=True, null=True)  # Field name made lowercase.
    de = models.TextField(db_column='DE', blank=True, null=True)  # Field name made lowercase.
    tamaño = models.TextField(db_column='Tamaño', blank=True, null=True)  # Field name made lowercase.
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)  # Field name made lowercase.
    radiomincurvatura = models.TextField(db_column='RadioMinCurvatura', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TipoCable'
