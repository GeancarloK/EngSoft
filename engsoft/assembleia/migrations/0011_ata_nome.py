# Generated by Django 4.2.11 on 2024-08-12 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assembleia', '0010_remove_ata_registro_registro_ata'),
    ]

    operations = [
        migrations.AddField(
            model_name='ata',
            name='nome',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
