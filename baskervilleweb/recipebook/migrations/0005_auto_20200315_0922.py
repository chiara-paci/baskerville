# Generated by Django 3.0.2 on 2020-03-15 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0004_auto_20200315_0917'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExecutionToolRelation',
            new_name='StepToolRelation',
        ),
    ]
