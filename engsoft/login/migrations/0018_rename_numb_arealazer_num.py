# Generated by Django 5.0.7 on 2024-08-11 21:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_alter_arealazer_fim_alter_arealazer_inicio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arealazer',
            old_name='numb',
            new_name='num',
        ),
    ]
