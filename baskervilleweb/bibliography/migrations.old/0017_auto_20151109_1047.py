# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0016_auto_20151109_1046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timepoint',
            options={'ordering': ['modifier', 'date']},
        ),
        migrations.RenameField(
            model_name='timepoint',
            old_name='y_date',
            new_name='date',
        ),
    ]
