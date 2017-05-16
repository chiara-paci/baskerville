# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0015_auto_20151109_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timepoint',
            name='y_date',
            field=models.IntegerField(),
        ),
    ]
