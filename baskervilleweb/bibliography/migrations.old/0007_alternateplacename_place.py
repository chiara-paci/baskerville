# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0006_auto_20151105_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternateplacename',
            name='place',
            field=models.ForeignKey(default=1, to='bibliography.Place'),
            preserve_default=False,
        ),
    ]
