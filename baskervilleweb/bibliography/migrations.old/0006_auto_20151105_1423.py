# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0005_auto_20151104_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternatePlaceName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
                ('note', models.CharField(max_length=65536, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='PlaceRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', models.ForeignKey(related_name='area_set', to='bibliography.Place')),
                ('place', models.ForeignKey(related_name='point_set', to='bibliography.Place')),
            ],
            options={
                'ordering': ['area', 'place'],
            },
        ),
        migrations.CreateModel(
            name='PlaceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.AlterModelOptions(
            name='timepoint',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='timespan',
            options={'ordering': ['begin', 'end']},
        ),
        migrations.AddField(
            model_name='place',
            name='type',
            field=models.ForeignKey(to='bibliography.PlaceType'),
        ),
    ]
