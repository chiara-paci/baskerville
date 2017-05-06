# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0027_auto_20151110_1708'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='author',
            table='bibliography_person',
        ),
    ]
