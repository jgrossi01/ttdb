# Generated by Django 5.1.7 on 2025-05-05 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_testresult_tooltip_a_testresult_tooltip_b'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testsession',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('in_progress', 'En curso'), ('completed', 'Terminado'), ('unmeasurable', 'No medible')], default='pending', max_length=20),
        ),
    ]
