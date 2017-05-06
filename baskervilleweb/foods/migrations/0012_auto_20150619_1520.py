# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0011_auto_20150619_1510'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name', 'vendor']},
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='added_sugar',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='alcohol',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
    ]
