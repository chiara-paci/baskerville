# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0005_micronutrientclass'),
    ]

    operations = [
        migrations.AddField(
            model_name='micronutrient',
            name='nutrient_class',
            field=models.ForeignKey(default=1, to='foods.MicroNutrientClass'),
            preserve_default=False,
        ),
    ]
