# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booktimespanrelation',
            name='book',
            field=models.OneToOneField(to='bibliography.Book'),
        ),
        migrations.AlterField(
            model_name='categorytimespanrelation',
            name='category',
            field=models.OneToOneField(to='bibliography.Category'),
        ),
    ]
