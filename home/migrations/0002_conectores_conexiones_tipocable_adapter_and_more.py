# Generated by Django 5.1.7 on 2025-05-27 19:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conectores',
            fields=[
                ('idconector', models.AutoField(db_column='IDConector', primary_key=True, serialize=False)),
                ('conector', models.TextField(blank=True, db_column='Conector', null=True)),
                ('link', models.TextField(blank=True, db_column='Link', null=True)),
                ('codigovuelo', models.TextField(blank=True, db_column='CodigoVuelo', null=True)),
                ('codigoingenieria', models.TextField(blank=True, db_column='CodigoIngenieria', null=True)),
                ('descripcion', models.TextField(blank=True, db_column='Descripcion', null=True)),
                ('link_file', models.TextField(blank=True, db_column='link_file', null=True)),
                ('listadepines', models.TextField(blank=True, db_column='ListadePines', null=True)),
                ('codigopinvuelo', models.TextField(blank=True, db_column='CodigoPinVuelo', null=True)),
                ('codigopiningenieria', models.TextField(blank=True, db_column='CodigoPinIngenieria', null=True)),
                ('datasheet', models.TextField(blank=True, db_column='datasheet', null=True)),
            ],
            options={
                'db_table': 'Conectores',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Conexiones',
            fields=[
                ('field_de_señal', models.TextField(db_column='# de Señal', primary_key=True, serialize=False)),
                ('nombre', models.TextField(blank=True, db_column='Nombre', null=True)),
                ('tipo_señal', models.TextField(blank=True, db_column='Tipo Señal', null=True)),
                ('descripcion', models.TextField(blank=True, db_column='Descripción', null=True)),
                ('señal_unidad', models.TextField(blank=True, db_column='Señal Unidad', null=True)),
                ('sistema', models.TextField(blank=True, db_column='Sistema', null=True)),
                ('subsistema', models.TextField(blank=True, db_column='Subsistema', null=True)),
                ('unidad', models.TextField(blank=True, db_column='Unidad', null=True)),
                ('modulo', models.TextField(blank=True, db_column='Modulo', null=True)),
                ('in_out', models.TextField(blank=True, db_column='IN/OUT', null=True)),
                ('origen', models.TextField(blank=True, db_column='Origen', null=True)),
                ('conector_orig', models.TextField(blank=True, db_column='Conector Orig', null=True)),
                ('pin_orig', models.TextField(blank=True, db_column='Pin Orig', null=True)),
                ('tipo_de_con_orig', models.TextField(blank=True, db_column='Tipo de Con Orig', null=True)),
                ('awg', models.TextField(blank=True, db_column='AWG', null=True)),
                ('longitud', models.TextField(blank=True, db_column='Longitud', null=True)),
                ('manguera', models.TextField(blank=True, db_column='Manguera', null=True)),
                ('shield', models.TextField(blank=True, db_column='Shield', null=True)),
                ('twisted', models.TextField(blank=True, db_column='Twisted', null=True)),
                ('señal_unidad1', models.TextField(blank=True, db_column='Señal Unidad1', null=True)),
                ('sistema1', models.TextField(blank=True, db_column='Sistema1', null=True)),
                ('subsistema1', models.TextField(blank=True, db_column='Subsistema1', null=True)),
                ('unidad1', models.TextField(blank=True, db_column='Unidad1', null=True)),
                ('modulo1', models.TextField(blank=True, db_column='Modulo1', null=True)),
                ('in_out1', models.TextField(blank=True, db_column='IN/OUT1', null=True)),
                ('destino', models.TextField(blank=True, db_column='Destino', null=True)),
                ('conector_dest', models.TextField(blank=True, db_column='Conector Dest', null=True)),
                ('pin_dest', models.TextField(blank=True, db_column='Pin Dest', null=True)),
                ('tipo_de_con_dest', models.TextField(blank=True, db_column='Tipo de Con Dest', null=True)),
                ('obsev', models.TextField(blank=True, db_column='Obsev', null=True)),
                ('interface', models.TextField(blank=True, db_column='Interface', null=True)),
                ('frec', models.TextField(blank=True, db_column='Frec', null=True)),
                ('imax', models.TextField(blank=True, db_column='Imax', null=True)),
                ('drop_voltage', models.TextField(blank=True, db_column='Drop Voltage', null=True)),
                ('clase_emi_emc', models.TextField(blank=True, db_column='Clase EMI/EMC', null=True)),
                ('clase_repuesto_field', models.TextField(blank=True, db_column='Clase(Repuesto)', null=True)),
                ('integrada_si_no_field', models.TextField(blank=True, db_column='Integrada(si/no)', null=True)),
                ('documento', models.TextField(blank=True, db_column='Documento', null=True)),
                ('activo_si_no_field', models.TextField(blank=True, db_column='activo(si/no)', null=True)),
                ('observacion_activo_si_no_field', models.TextField(blank=True, db_column='Observacion(activo si/no)', null=True)),
                ('PEM_Polaridad', models.TextField(blank=True, db_column='PEM_Polaridad', null=True)),
                ('PEM_Telemetria', models.TextField(blank=True, db_column='PEM_Telemetria', null=True)),
                ('PEM_tipo_señal', models.TextField(blank=True, db_column='PEM_tiposeñal', null=True)),
            ],
            options={
                'db_table': 'Conexiones',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tipocable',
            fields=[
                ('idcable', models.AutoField(db_column='IDCable', primary_key=True, serialize=False)),
                ('nombre', models.TextField(blank=True, db_column='Nombre', null=True)),
                ('nombrecable', models.TextField(blank=True, db_column='NombreCable', null=True)),
                ('nombrealambre', models.TextField(blank=True, db_column='NombreAlambre', null=True)),
                ('de', models.TextField(blank=True, db_column='DE', null=True)),
                ('tamaño', models.TextField(blank=True, db_column='Tamaño', null=True)),
                ('descripcion', models.TextField(blank=True, db_column='Descripcion', null=True)),
                ('radiomincurvatura', models.TextField(blank=True, db_column='RadioMinCurvatura', null=True)),
            ],
            options={
                'db_table': 'TipoCable',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Adapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConnectionConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_port', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MDBFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('file', models.FileField(upload_to='mdb_files/')),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=50)),
                ('created_records', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RelayCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('bus', models.IntegerField()),
                ('device', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TestSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connector', models.CharField(max_length=50)),
                ('test_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('in_progress', 'En curso'), ('completed', 'Terminado'), ('unmeasurable', 'No medible')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AdapterConnector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connector_type', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=50)),
                ('pin_qty', models.PositiveIntegerField()),
                ('connector_side', models.CharField(choices=[('pxi-side', 'Lado PXI'), ('test-side', 'Lado test')], default='test-side', max_length=50)),
                ('adapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connectors', to='home.adapter')),
            ],
            options={
                'ordering': ['adapter', 'label'],
                'unique_together': {('adapter', 'label')},
            },
        ),
        migrations.CreateModel(
            name='FixedConnector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connector_type', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=50)),
                ('pin_qty', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['label'],
                'unique_together': {('connector_type', 'label')},
            },
        ),
        migrations.CreateModel(
            name='RelayPinMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pxi_channel_type', models.CharField(blank=True, choices=[('U', 'Input (1-74)'), ('M', 'Output (1-74)'), ('F', 'Fault MUX (1-8)'), ('MON', 'Monitor (1-2)'), ('GND', 'GND (1-2)'), ('', 'No definido')], max_length=10, null=True)),
                ('pxi_channel', models.PositiveIntegerField(blank=True, null=True)),
                ('to_test_pin', models.PositiveIntegerField(blank=True, null=True)),
                ('relay_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relay_pin_maps', to='home.relaycard')),
                ('test_connector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='relay_mapped_pins', to='home.fixedconnector')),
            ],
            options={
                'ordering': ['relay_card', 'pxi_channel_type', 'pxi_channel'],
                'unique_together': {('relay_card', 'pxi_channel_type', 'pxi_channel'), ('test_connector', 'to_test_pin')},
            },
        ),
        migrations.CreateModel(
            name='TestStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage_number', models.PositiveIntegerField()),
                ('stage_type', models.CharField(max_length=50)),
                ('connector_dest', models.CharField(max_length=50)),
                ('instructions', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('completed', 'Terminado'), ('unmeasurable', 'No medible')], default='pending', max_length=20)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='home.testsession')),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal_id', models.IntegerField()),
                ('signal_name', models.CharField(max_length=50)),
                ('conector_orig', models.CharField(max_length=50)),
                ('pin_a', models.CharField(max_length=50)),
                ('tooltip_a', models.CharField(blank=True, max_length=50, null=True)),
                ('conector_dest', models.CharField(max_length=50)),
                ('pin_b', models.CharField(max_length=50)),
                ('tooltip_b', models.CharField(blank=True, max_length=50, null=True)),
                ('min_exp_value', models.CharField(max_length=50)),
                ('max_exp_value', models.CharField(max_length=50)),
                ('measured_value', models.CharField(blank=True, max_length=50, null=True)),
                ('result', models.CharField(choices=[('pending', 'Pendiente'), ('pass', 'OK'), ('fail', 'NO OK')], default='pending', max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='home.teststage')),
            ],
        ),
        migrations.CreateModel(
            name='AdapterPinMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_pxi_pin', models.PositiveIntegerField()),
                ('to_test_pin', models.PositiveIntegerField()),
                ('adapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pin_maps', to='home.adapter')),
                ('pxi_connector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pxi_mapped_pins', to='home.adapterconnector')),
                ('test_connector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_mapped_pins', to='home.adapterconnector')),
                ('relay_pin_map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adapter_mappings', to='home.relaypinmap')),
            ],
            options={
                'ordering': ['adapter', 'relay_pin_map'],
                'unique_together': {('adapter', 'pxi_connector', 'to_pxi_pin'), ('adapter', 'relay_pin_map'), ('adapter', 'test_connector', 'to_test_pin')},
            },
        ),
    ]
