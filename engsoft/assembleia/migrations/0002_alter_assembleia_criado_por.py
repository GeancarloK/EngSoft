# Generated by Django 5.0.7 on 2024-08-09 03:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assembleia', '0001_initial'),
        ('login', '0012_alter_notpessoa_email_alter_pessoa_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assembleia',
            name='criado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.construtora'),
        ),
    ]
