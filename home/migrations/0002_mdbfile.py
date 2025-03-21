# Generated by Django 4.2.8 on 2025-03-13 15:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MDBFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='mdb_files/')),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=50)),
                ('status', models.CharField(default='Pendiente', max_length=50)),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
