# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0010_usdanndfood'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsdaNndFoodLangualRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('food', models.ForeignKey(to='foods.UsdaNndFood')),
            ],
        ),
        migrations.CreateModel(
            name='UsdaNndLangual',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usda_id', models.CharField(max_length=1024)),
                ('description', models.CharField(max_length=1024)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='added_sugar',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='alcohol',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usdanndfoodlangualrelation',
            name='langual',
            field=models.ForeignKey(to='foods.UsdaNndLangual'),
        ),
    ]
