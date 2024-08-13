# Generated by Django 5.0.7 on 2024-08-09 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assembleia', '0003_remove_votacao_pauta_remove_assembleia_descricao_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assembleia',
            name='status',
            field=models.CharField(choices=[('criada', 'Criada'), ('iniciada', 'Iniciada'), ('finalizada', 'Finalizada'), ('entregue', 'Entregue')], default='criada', max_length=10),
        ),
    ]
