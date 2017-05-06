# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0032_auto_20151111_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryPersonRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='bibliography.Category')),
                ('person', models.ForeignKey(to='bibliography.Person')),
            ],
        ),
    ]
