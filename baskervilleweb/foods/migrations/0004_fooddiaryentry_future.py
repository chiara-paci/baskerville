# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_micronutrient_rda_max'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooddiaryentry',
            name='future',
            field=models.BooleanField(default=False),
        ),
    ]
