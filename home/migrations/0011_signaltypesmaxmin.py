# Generated by Django 5.1.7 on 2025-07-10 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_testresult_signal_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignalTypesMaxMin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('min', models.IntegerField(blank=True, null=True)),
                ('max', models.IntegerField(blank=True, null=True)),
                ('unit', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
    ]
