# -*- encoding: utf-8 -*-
from django.db import models


class Conectores(models.Model):
    idconector = models.AutoField(db_column='IDConector', primary_key=True)  # Clave primaria
    conector = models.TextField(db_column='Conector', blank=True, null=True)
    link = models.TextField(db_column='Link', blank=True, null=True)
    codigovuelo = models.TextField(db_column='CodigoVuelo', blank=True, null=True)
    codigoingenieria = models.TextField(db_column='CodigoIngenieria', blank=True, null=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    link_file = models.TextField(db_column='link_file', blank=True, null=True)
    listadepines = models.TextField(db_column='ListadePines', blank=True, null=True)
    codigopinvuelo = models.TextField(db_column='CodigoPinVuelo', blank=True, null=True)
    codigopiningenieria = models.TextField(db_column='CodigoPinIngenieria', blank=True, null=True)
    datasheet = models.TextField(db_column='datasheet', blank=True, null=True)

    class Meta:
        db_table = 'Conectores'  # Nombre de la tabla en la DB
        managed = False


class Conexiones(models.Model):
    field_de_señal = models.AutoField(db_column='# de Señal', primary_key=True)  # Clave primaria
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)
    tipo_señal = models.TextField(db_column='Tipo Señal', blank=True, null=True)
    descripcion = models.TextField(db_column='Descripción', blank=True, null=True)
    señal_unidad = models.TextField(db_column='Señal Unidad', blank=True, null=True)
    sistema = models.TextField(db_column='Sistema', blank=True, null=True)
    subsistema = models.TextField(db_column='Subsistema', blank=True, null=True)
    unidad = models.TextField(db_column='Unidad', blank=True, null=True)
    modulo = models.TextField(db_column='Modulo', blank=True, null=True)
    in_out = models.TextField(db_column='IN/OUT', blank=True, null=True)
    origen = models.TextField(db_column='Origen', blank=True, null=True)
    conector_orig = models.TextField(db_column='Conector Orig', blank=True, null=True)
    pin_orig = models.TextField(db_column='Pin Orig', blank=True, null=True)
    tipo_de_con_orig = models.TextField(db_column='Tipo de Con Orig', blank=True, null=True)
    awg = models.TextField(db_column='AWG', blank=True, null=True)
    longitud = models.TextField(db_column='Longitud', blank=True, null=True)
    manguera = models.TextField(db_column='Manguera', blank=True, null=True)
    shield = models.TextField(db_column='Shield', blank=True, null=True)
    twisted = models.TextField(db_column='Twisted', blank=True, null=True)
    señal_unidad1 = models.TextField(db_column='Señal Unidad1', blank=True, null=True)
    sistema1 = models.TextField(db_column='Sistema1', blank=True, null=True)
    subsistema1 = models.TextField(db_column='Subsistema1', blank=True, null=True)
    unidad1 = models.TextField(db_column='Unidad1', blank=True, null=True)
    modulo1 = models.TextField(db_column='Modulo1', blank=True, null=True)
    in_out1 = models.TextField(db_column='IN/OUT1', blank=True, null=True)
    destino = models.TextField(db_column='Destino', blank=True, null=True)
    conector_dest = models.TextField(db_column='Conector Dest', blank=True, null=True)
    pin_dest = models.TextField(db_column='Pin Dest', blank=True, null=True)
    tipo_de_con_dest = models.TextField(db_column='Tipo de Con Dest', blank=True, null=True)
    obsev = models.TextField(db_column='Obsev', blank=True, null=True)
    interface = models.TextField(db_column='Interface', blank=True, null=True)
    frec = models.TextField(db_column='Frec', blank=True, null=True)
    imax = models.TextField(db_column='Imax', blank=True, null=True)
    drop_voltage = models.TextField(db_column='Drop Voltage', blank=True, null=True)
    clase_emi_emc = models.TextField(db_column='Clase EMI/EMC', blank=True, null=True)
    clase_repuesto_field = models.TextField(db_column='Clase(Repuesto)', blank=True, null=True)
    integrada_si_no_field = models.TextField(db_column='Integrada(si/no)', blank=True, null=True)
    documento = models.TextField(db_column='Documento', blank=True, null=True)
    activo_si_no_field = models.TextField(db_column='activo(si/no)', blank=True, null=True)
    observacion_activo_si_no_field = models.TextField(db_column='Observacion(activo si/no)', blank=True, null=True)
    PEM_Polaridad = models.TextField(db_column='PEM_Polaridad', blank=True, null=True)
    PEM_Telemetria = models.TextField(db_column='PEM_Telemetria', blank=True, null=True)
    PEM_tipo_señal = models.TextField(db_column='PEM_tipo_señal', blank=True, null=True)

    class Meta:
        db_table = 'Conexiones'
        managed = False


class Tipocable(models.Model):
    idcable = models.AutoField(db_column='IDCable', primary_key=True)  # Clave primaria
    nombre = models.TextField(db_column='Nombre', blank=True, null=True)
    nombrecable = models.TextField(db_column='NombreCable', blank=True, null=True)
    nombrealambre = models.TextField(db_column='NombreAlambre', blank=True, null=True)
    de = models.TextField(db_column='DE', blank=True, null=True)
    tamaño = models.TextField(db_column='Tamaño', blank=True, null=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    radiomincurvatura = models.TextField(db_column='RadioMinCurvatura', blank=True, null=True)

    class Meta:
        db_table = 'TipoCable'
        managed = False
