# Generated by Django 4.2.11 on 2024-08-12 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0025_alter_arealazer_options_alter_arealazer_fim_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='arealazer',
            name='bloqueado',
            field=models.BooleanField(default=False, verbose_name='Bloqueado'),
        ),
    ]
