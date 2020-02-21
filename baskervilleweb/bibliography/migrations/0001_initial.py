# Generated by Django 3.0.2 on 2020-02-21 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('cover_name', models.BooleanField(default=False)),
                ('action', models.CharField(blank=True, default='', max_length=1024)),
                ('pos', models.IntegerField(unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn_ced', models.CharField(max_length=9)),
                ('isbn_book', models.CharField(max_length=9)),
                ('isbn_crc10', models.CharField(default='Y', editable=False, max_length=1)),
                ('isbn_crc13', models.CharField(default='Y', editable=False, max_length=1)),
                ('isbn_cache10', models.CharField(default='', editable=False, max_length=20)),
                ('isbn_cache13', models.CharField(default='', editable=False, max_length=20)),
                ('title', models.CharField(max_length=4096)),
                ('year', models.IntegerField()),
                ('year_ipotetic', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['title', 'year', 'publisher'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096, unique=True)),
                ('label', models.SlugField(editable=False, max_length=4096, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DateModifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=1024)),
                ('reverse', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['pos'],
            },
        ),
        migrations.CreateModel(
            name='IssueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageFamily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageVarietyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='NameFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('pattern', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ['label'],
            },
        ),
        migrations.CreateModel(
            name='NameFormatCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('preferred', models.BooleanField(default=False)),
                ('list_format', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='list_format_set', to='bibliography.NameFormat')),
                ('long_format', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='long_format_set', to='bibliography.NameFormat')),
                ('ordering_format', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordering_format_set', to='bibliography.NameFormat')),
                ('short_format', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='short_format_set', to='bibliography.NameFormat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NameType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'bibliography_person',
                'ordering': ['cache'],
            },
        ),
        migrations.CreateModel(
            name='PersonCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('long_name', models.CharField(default='-', max_length=4096)),
                ('short_name', models.CharField(default='-', max_length=4096)),
                ('list_name', models.CharField(default='-', max_length=4096)),
                ('ordering_name', models.CharField(default='-', max_length=4096)),
            ],
            options={
                'db_table': 'bibliography_personcache',
                'ordering': ['ordering_name'],
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PlaceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issn', models.CharField(max_length=128)),
                ('issn_crc', models.CharField(default='Y', editable=False, max_length=1)),
                ('title', models.CharField(max_length=4096)),
                ('date_format', models.CharField(default='%Y-%m-%d', max_length=4096)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
                ('full_name', models.CharField(blank=True, max_length=4096)),
                ('url', models.CharField(default='--', max_length=4096)),
                ('note', models.TextField(blank=True, default='')),
                ('alias', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublisherAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['city'],
            },
        ),
        migrations.CreateModel(
            name='PublisherState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RepositoryCacheBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(max_length=13, unique=True)),
                ('publisher', models.CharField(default=' ', max_length=4096)),
                ('year', models.CharField(blank=True, default=' ', max_length=4096)),
                ('title', models.CharField(default=' ', max_length=4096)),
                ('city', models.CharField(default=' ', max_length=4096)),
                ('indb', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['isbn'],
            },
        ),
        migrations.CreateModel(
            name='RepositoryFailedIsbn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn10', models.CharField(max_length=4096)),
                ('isbn13', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['isbn10'],
            },
        ),
        migrations.CreateModel(
            name='TimePoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.IntegerField()),
                ('modifier', models.ForeignKey(blank=True, default=0, on_delete=django.db.models.deletion.PROTECT, to='bibliography.DateModifier')),
            ],
            options={
                'ordering': ['modifier', 'date'],
                'unique_together': {('modifier', 'date')},
            },
        ),
        migrations.CreateModel(
            name='VolumeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('read_as', models.CharField(default='', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=256)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSpan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=4096)),
                ('begin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='begin_set', to='bibliography.TimePoint')),
                ('end', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='end_set', to='bibliography.TimePoint')),
            ],
            options={
                'ordering': ['begin', 'end'],
            },
        ),
        migrations.CreateModel(
            name='TextsCdrom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('books', models.ManyToManyField(blank=True, to='bibliography.Book')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RepositoryCacheAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=4096)),
                ('role', models.CharField(max_length=4096)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.RepositoryCacheBook')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublisherIsbn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(db_index=True, max_length=4096, unique=True)),
                ('preferred', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher')),
            ],
            options={
                'ordering': ['isbn'],
            },
        ),
        migrations.CreateModel(
            name='PublisherAddressPublisherRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.PositiveIntegerField()),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.PublisherAddress')),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='publisheraddress',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.PublisherState'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='addresses',
            field=models.ManyToManyField(blank=True, through='bibliography.PublisherAddressPublisherRelation', to='bibliography.PublisherAddress'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='isbns',
            field=models.ManyToManyField(blank=True, to='bibliography.PublisherIsbn'),
        ),
        migrations.AddField(
            model_name='publication',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher'),
        ),
        migrations.AddField(
            model_name='publication',
            name='volume_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.VolumeType'),
        ),
        migrations.CreateModel(
            name='PlaceRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='place_set', to='bibliography.Place')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='area_set', to='bibliography.Place')),
            ],
            options={
                'ordering': ['area', 'place'],
            },
        ),
        migrations.AddField(
            model_name='place',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.PlaceType'),
        ),
        migrations.CreateModel(
            name='PersonNameRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, default='-', max_length=4096)),
                ('name_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.NameType')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Person')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='cache',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='bibliography.PersonCache'),
        ),
        migrations.AddField(
            model_name='person',
            name='format_collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.NameFormatCollection'),
        ),
        migrations.AddField(
            model_name='person',
            name='names',
            field=models.ManyToManyField(blank=True, through='bibliography.PersonNameRelation', to='bibliography.NameType'),
        ),
        migrations.CreateModel(
            name='MigrPublisherRiviste',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registro', models.CharField(max_length=4096)),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageVariety',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=4096)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Language')),
                ('type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='bibliography.LanguageVarietyType')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageFamilyRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.LanguageFamily')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Language')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageFamilyFamilyRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_set', to='bibliography.LanguageFamily')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='child_set', to='bibliography.LanguageFamily')),
            ],
            options={
                'ordering': ['parent', 'child'],
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issn_num', models.CharField(max_length=8)),
                ('number', models.CharField(max_length=256)),
                ('title', models.CharField(blank=True, default='', max_length=4096)),
                ('date', models.DateField()),
                ('date_ipotetic', models.BooleanField(default=False)),
                ('issue_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.IssueType')),
                ('volume', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Volume')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='CategoryTreeNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('node_id', models.CharField(max_length=4096, unique=True)),
                ('has_children', models.BooleanField()),
                ('level', models.PositiveIntegerField()),
                ('label', models.CharField(editable=False, max_length=4096)),
                ('label_children', models.CharField(editable=False, max_length=4096)),
                ('is_category', models.BooleanField(editable=False)),
                ('num_objects', models.PositiveIntegerField(editable=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['node_id'],
            },
        ),
        migrations.CreateModel(
            name='CategoryTimeSpanRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Category')),
                ('time_span', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.TimeSpan')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_set', to='bibliography.Category')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='child_set', to='bibliography.Category')),
            ],
            options={
                'ordering': ['parent', 'child'],
            },
        ),
        migrations.CreateModel(
            name='CategoryPlaceRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Category')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Place')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryPersonRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Category')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Person')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryLanguageRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Category')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.LanguageVariety')),
            ],
        ),
        migrations.CreateModel(
            name='BookSerieWithoutIsbn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn_ced', models.CharField(db_index=True, max_length=9)),
                ('isbn_book_prefix', models.CharField(db_index=True, max_length=9)),
                ('title', models.CharField(max_length=4096)),
                ('title_prefix', models.CharField(blank=True, default='', max_length=4096)),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(blank=True, to='bibliography.Category'),
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Publisher'),
        ),
        migrations.CreateModel(
            name='AuthorRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(db_index=True, editable=False)),
                ('year_label', models.CharField(editable=False, max_length=10)),
                ('title', models.CharField(max_length=4096)),
                ('author_role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.AuthorRole')),
                ('content_type', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['year'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=4096)),
                ('page_begin', models.CharField(blank=True, default='x', max_length=10)),
                ('page_end', models.CharField(blank=True, default='x', max_length=10)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Issue')),
            ],
        ),
        migrations.CreateModel(
            name='AlternatePlaceName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
                ('note', models.CharField(blank=True, max_length=65536)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Place')),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('bibliography.person',),
        ),
        migrations.CreateModel(
            name='MigrAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod', models.CharField(default='-', max_length=1)),
                ('ind', models.IntegerField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Author')),
            ],
        ),
        migrations.CreateModel(
            name='IssueAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Issue')),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.AddField(
            model_name='issue',
            name='authors',
            field=models.ManyToManyField(blank=True, through='bibliography.IssueAuthorRelation', to='bibliography.Author'),
        ),
        migrations.CreateModel(
            name='BookAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Book')),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(blank=True, through='bibliography.BookAuthorRelation', to='bibliography.Author'),
        ),
        migrations.AddField(
            model_name='authorrelation',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Author'),
        ),
        migrations.CreateModel(
            name='ArticleAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bibliography.Article')),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(blank=True, through='bibliography.ArticleAuthorRelation', to='bibliography.Author'),
        ),
        migrations.AlterIndexTogether(
            name='book',
            index_together={('isbn_ced', 'isbn_book')},
        ),
    ]
