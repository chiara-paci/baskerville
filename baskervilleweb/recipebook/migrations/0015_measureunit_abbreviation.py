# Generated by Django 3.0.2 on 2020-03-15 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0014_measureunit_apply_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='measureunit',
            name='abbreviation',
            field=models.CharField(default='-', max_length=1024),
            preserve_default=False,
        ),
    ]
