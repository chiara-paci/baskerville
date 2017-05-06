# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0017_auto_20151109_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='datemodifier',
            name='reverse',
            field=models.BooleanField(default=False),
        ),
    ]
