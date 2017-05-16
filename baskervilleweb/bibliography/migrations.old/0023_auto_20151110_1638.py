# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0022_auto_20151110_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonNameRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(default=b'-', max_length=4096)),
            ],
        ),
        migrations.RemoveField(
            model_name='authornamerelation',
            name='author',
        ),
        migrations.RemoveField(
            model_name='authornamerelation',
            name='name_type',
        ),
        migrations.RemoveField(
            model_name='author',
            name='names',
        ),
        migrations.DeleteModel(
            name='AuthorNameRelation',
        ),
        migrations.AddField(
            model_name='personnamerelation',
            name='author',
            field=models.ForeignKey(to='bibliography.Author'),
        ),
        migrations.AddField(
            model_name='personnamerelation',
            name='name_type',
            field=models.ForeignKey(to='bibliography.NameType'),
        ),
    ]
