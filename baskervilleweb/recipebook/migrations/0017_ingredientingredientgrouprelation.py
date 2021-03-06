# Generated by Django 3.0.2 on 2020-03-20 04:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0016_ingredientgroup_preparation'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientIngredientGroupRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipebook.IngredientGroup')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipebook.Ingredient')),
            ],
        ),
    ]
