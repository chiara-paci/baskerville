# Generated by Django 3.0 on 2020-12-28 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0017_auto_20201228_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='exifdatum',
            name='photod',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='archive.PhotoD'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photometadatum',
            name='photod',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='archive.PhotoD'),
            preserve_default=False,
        ),
    ]