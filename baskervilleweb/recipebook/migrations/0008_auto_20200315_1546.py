# Generated by Django 3.0.2 on 2020-03-15 14:46

from django.db import migrations, models
import django.db.models.deletion
import recipebook.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0007_auto_20200315_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='tools',
            field=models.ManyToManyField(blank=True, through='recipebook.StepToolRelation', to='recipebook.Tool'),
        ),
        migrations.AlterField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(default=recipebook.models.get_bulk_product_vendor, on_delete=django.db.models.deletion.PROTECT, to='recipebook.Vendor'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='name',
            field=models.CharField(max_length=4096, unique=True),
        ),
    ]
