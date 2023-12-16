# Generated by Django 3.2 on 2023-12-16 21:16

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(db_index=True, validators=[reviews.validators.validate_year], verbose_name='Год выпуска'),
        ),
    ]
