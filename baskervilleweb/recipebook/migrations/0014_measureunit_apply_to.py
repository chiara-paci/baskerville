# Generated by Django 3.0.2 on 2020-03-15 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0013_auto_20200315_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='measureunit',
            name='apply_to',
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
    ]
