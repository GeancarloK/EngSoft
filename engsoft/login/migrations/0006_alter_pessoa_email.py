# Generated by Django 4.2.11 on 2024-08-04 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_pessoa_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='email',
            field=models.CharField(default='Sem e-mail', max_length=200),
        ),
    ]
