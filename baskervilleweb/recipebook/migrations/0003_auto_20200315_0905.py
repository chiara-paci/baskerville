# Generated by Django 3.0.2 on 2020-03-15 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0002_auto_20200221_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='execution_tools',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredient_tools',
        ),
    ]
