# Generated by Django 3.0.2 on 2020-03-20 04:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0015_measureunit_abbreviation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientgroup',
            name='preparation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='recipebook.StepSequence'),
        ),
    ]
