# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0012_auto_20150619_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='fiber',
            field=models.FloatField(default=0, verbose_name=b'fiber (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='potassium',
            field=models.FloatField(default=0, verbose_name=b'potassium (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='salt',
            field=models.FloatField(default=0, verbose_name=b'salt (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='sodium',
            field=models.FloatField(default=0, verbose_name=b'sodium (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='water',
            field=models.FloatField(default=0, verbose_name=b'water (ml)', validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
    ]
