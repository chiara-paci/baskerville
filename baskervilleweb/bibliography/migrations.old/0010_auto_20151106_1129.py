# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0009_auto_20151105_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageFamilyFamilyRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name='child_set', to='bibliography.LanguageFamily')),
                ('parent', models.ForeignKey(related_name='parent_set', to='bibliography.LanguageFamily')),
            ],
            options={
                'ordering': ['parent', 'child'],
            },
        ),
        migrations.CreateModel(
            name='LanguageFamilyRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family', models.ForeignKey(to='bibliography.LanguageFamily')),
                ('language', models.ForeignKey(to='bibliography.Language')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageVariety',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
                ('language', models.ForeignKey(to='bibliography.Language')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageVarietyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.AlterModelOptions(
            name='categoryrelation',
            options={'ordering': ['parent', 'child']},
        ),
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['name']},
        ),
        migrations.RenameField(
            model_name='categoryrelation',
            old_name='father',
            new_name='parent',
        ),
        migrations.AlterField(
            model_name='categoryrelation',
            name='child',
            field=models.ForeignKey(related_name='parent_set', to='bibliography.Category'),
        ),
        migrations.AddField(
            model_name='languagevariety',
            name='type',
            field=models.ForeignKey(default=1, to='bibliography.LanguageVarietyType'),
        ),
    ]
