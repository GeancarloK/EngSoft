# Generated by Django 5.0.7 on 2024-08-11 21:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0022_rename_inicio_arealazer_start'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arealazer',
            old_name='start',
            new_name='fim',
        ),
        migrations.RenameField(
            model_name='arealazer',
            old_name='num',
            new_name='numb',
        ),
        migrations.RemoveField(
            model_name='arealazer',
            name='tempo',
        ),
        migrations.AddField(
            model_name='arealazer',
            name='inicio',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
