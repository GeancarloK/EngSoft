# Generated by Django 5.0.7 on 2024-08-11 21:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0019_remove_arealazer_fim_arealazer_tempo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arealazer',
            name='inicio',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
