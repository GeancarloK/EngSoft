# Generated by Django 4.2.11 on 2024-08-04 17:03

from django.db import migrations, models
import login.models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_condominio_nro_acad_condominio_nro_andares_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='andar',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='apt',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='bloco',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='CPF',
            field=models.CharField(default='00000000000', max_length=11, validators=[login.models.validate_cpf]),
        ),
    ]
