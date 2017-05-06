# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0003_categorytype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booktimespanrelation',
            name='book',
        ),
        migrations.RemoveField(
            model_name='booktimespanrelation',
            name='time_span',
        ),
        migrations.DeleteModel(
            name='CategoryType',
        ),
        migrations.DeleteModel(
            name='BookTimeSpanRelation',
        ),
    ]
