# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0018_frequentdiaryentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frequentdiaryentry',
            name='user',
        ),
    ]
