# Generated by Django 3.2 on 2023-12-13 14:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmation_code', to=settings.AUTH_USER_MODEL),
        ),
    ]
