# Generated by Django 3.2 on 2023-12-16 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'admin'), ('user', 'user'), ('moderator', 'moderator')], default='user', max_length=150, verbose_name='Роль'),
        ),
    ]
