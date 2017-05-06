# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0028_auto_20151110_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personnamerelation',
            old_name='author',
            new_name='person',
        ),
    ]
