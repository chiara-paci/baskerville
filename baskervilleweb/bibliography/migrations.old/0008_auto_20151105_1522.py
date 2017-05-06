# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0007_alternateplacename_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryPlaceRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='bibliography.Category')),
                ('place', models.ForeignKey(to='bibliography.Place')),
            ],
        ),
        migrations.AlterField(
            model_name='placerelation',
            name='area',
            field=models.ForeignKey(related_name='place_set', to='bibliography.Place'),
        ),
        migrations.AlterField(
            model_name='placerelation',
            name='place',
            field=models.ForeignKey(related_name='area_set', to='bibliography.Place'),
        ),
    ]
