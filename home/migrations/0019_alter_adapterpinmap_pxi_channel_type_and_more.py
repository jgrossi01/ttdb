# Generated by Django 5.1.7 on 2025-05-19 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_alter_adapterconnection_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adapterpinmap',
            name='pxi_channel_type',
            field=models.CharField(blank=True, choices=[('U', 'Input'), ('M', 'Output')], default='U', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='physicalconnector',
            name='connector_side',
            field=models.CharField(choices=[('pxi-side', 'Lado PXI'), ('test-side', 'Lado test')], default='test-side', max_length=50),
        ),
    ]
