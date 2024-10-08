# Generated by Django 4.2.11 on 2024-08-04 19:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import login.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('login', '0006_alter_pessoa_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotPessoa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('email', models.CharField(default='Sem e-mail', max_length=200)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('CPF', models.CharField(default='00000000000', max_length=11, validators=[login.models.validate_cpf])),
                ('pendencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.condominio')),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'not_pessoas',
            },
        ),
    ]
