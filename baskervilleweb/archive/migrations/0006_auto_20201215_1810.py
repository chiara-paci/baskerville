# Generated by Django 3.0 on 2020-12-15 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_document_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='label',
            field=models.SlugField(unique=True),
        ),
    ]
