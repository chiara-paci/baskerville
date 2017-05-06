# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0021_auto_20151110_1605'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='personcache',
            table='bibliography_personcache',
        ),
    ]
