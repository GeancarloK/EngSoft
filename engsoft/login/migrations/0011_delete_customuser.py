# Generated by Django 5.0.7 on 2024-08-05 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0010_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
