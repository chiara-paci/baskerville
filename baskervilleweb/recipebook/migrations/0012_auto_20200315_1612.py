# Generated by Django 3.0.2 on 2020-03-15 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0011_remove_step_tools'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='food',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='foodcategory',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='ingredientalternative',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='ingredientgroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='recipecategory',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='recipelabel',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='recipeset',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='retailer',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='stepsequence',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='tool',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='vendor',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='step',
            name='pos',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterOrderWithRespectTo(
            name='stepsequence',
            order_with_respect_to=None,
        ),
    ]