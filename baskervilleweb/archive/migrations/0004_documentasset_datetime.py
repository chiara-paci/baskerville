# Generated by Django 3.0 on 2020-12-13 16:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0003_document_documentasset_documentassetmetadatum_documentcollection_documentmetadatum'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentasset',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
