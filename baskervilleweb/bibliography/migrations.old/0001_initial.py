# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=4096)),
                ('page_begin', models.CharField(default=b'x', max_length=10, blank=True)),
                ('page_end', models.CharField(default=b'x', max_length=10, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ['cache'],
            },
        ),
        migrations.CreateModel(
            name='AuthorCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('long_name', models.CharField(default=b'-', max_length=4096)),
                ('short_name', models.CharField(default=b'-', max_length=4096)),
                ('list_name', models.CharField(default=b'-', max_length=4096)),
                ('ordering_name', models.CharField(default=b'-', max_length=4096)),
            ],
            options={
                'ordering': ['ordering_name'],
            },
        ),
        migrations.CreateModel(
            name='AuthorNameRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(default=b'-', max_length=4096)),
                ('author', models.ForeignKey(to='bibliography.Author')),
            ],
        ),
        migrations.CreateModel(
            name='AuthorRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ['year'],
            },
        ),
        migrations.CreateModel(
            name='AuthorRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('cover_name', models.BooleanField(default=False)),
                ('action', models.CharField(default=b'', max_length=1024, blank=True)),
                ('pos', models.IntegerField(unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn_ced', models.CharField(max_length=9, db_index=True)),
                ('isbn_book', models.CharField(max_length=9, db_index=True)),
                ('isbn_crc10', models.CharField(default=b'Y', max_length=1, editable=False)),
                ('isbn_crc13', models.CharField(default=b'Y', max_length=1, editable=False)),
                ('isbn_cache10', models.CharField(default=b'', max_length=20, editable=False)),
                ('isbn_cache13', models.CharField(default=b'', max_length=20, editable=False)),
                ('title', models.CharField(max_length=4096)),
                ('year', models.IntegerField()),
            ],
            options={
                'ordering': ['title', 'year', 'publisher'],
            },
        ),
        migrations.CreateModel(
            name='BookSerieWithoutIsbn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn_ced', models.CharField(max_length=9, db_index=True)),
                ('isbn_book_prefix', models.CharField(max_length=9, db_index=True)),
                ('title', models.CharField(max_length=4096)),
                ('title_prefix', models.CharField(default=b'', max_length=4096, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BookTimeSpanRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book', models.ForeignKey(to='bibliography.Book', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=4096)),
                ('label', models.SlugField(unique=True, max_length=4096, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CategoryRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name='father_set', to='bibliography.Category')),
                ('father', models.ForeignKey(related_name='child_set', to='bibliography.Category')),
            ],
            options={
                'ordering': ['father', 'child'],
            },
        ),
        migrations.CreateModel(
            name='CategoryTimeSpanRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='bibliography.Category', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryTreeNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('node_id', models.CharField(unique=True, max_length=4096)),
                ('has_children', models.BooleanField()),
                ('level', models.PositiveIntegerField()),
                ('label', models.CharField(max_length=4096, editable=False)),
                ('label_children', models.CharField(max_length=4096, editable=False)),
                ('is_category', models.BooleanField(editable=False)),
                ('num_objects', models.PositiveIntegerField(editable=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['node_id'],
            },
        ),
        migrations.CreateModel(
            name='DateModifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='DateSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issn_num', models.CharField(max_length=8)),
                ('number', models.CharField(max_length=256)),
                ('title', models.CharField(default=b'', max_length=4096, blank=True)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='IssueType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MigrAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cod', models.CharField(default=b'-', max_length=1, db_index=True)),
                ('ind', models.IntegerField(db_index=True)),
                ('author', models.ForeignKey(to='bibliography.Author')),
            ],
        ),
        migrations.CreateModel(
            name='MigrPublisherRiviste',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registro', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='NameFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('list_format', models.ForeignKey(related_name='list_format_set', to='bibliography.NameFormat')),
                ('long_format', models.ForeignKey(related_name='long_format_set', to='bibliography.NameFormat')),
                ('ordering_format', models.ForeignKey(related_name='ordering_format_set', to='bibliography.NameFormat')),
                ('short_format', models.ForeignKey(related_name='short_format_set', to='bibliography.NameFormat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NameType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issn', models.CharField(max_length=128)),
                ('issn_crc', models.CharField(default=b'Y', max_length=1, editable=False)),
                ('title', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
                ('full_name', models.CharField(max_length=4096, blank=True)),
                ('url', models.CharField(default=b'--', max_length=4096)),
                ('note', models.TextField(default=b'', blank=True)),
                ('alias', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublisherAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['city'],
            },
        ),
        migrations.CreateModel(
            name='PublisherAddressPublisherRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pos', models.PositiveIntegerField()),
                ('address', models.ForeignKey(to='bibliography.PublisherAddress')),
                ('publisher', models.ForeignKey(to='bibliography.Publisher')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublisherIsbn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn', models.CharField(unique=True, max_length=4096)),
                ('preferred', models.ForeignKey(blank=True, editable=False, to='bibliography.Publisher')),
            ],
            options={
                'ordering': ['isbn'],
            },
        ),
        migrations.CreateModel(
            name='PublisherState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RepositoryCacheAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pos', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=4096)),
                ('role', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RepositoryCacheBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn', models.CharField(unique=True, max_length=13)),
                ('publisher', models.CharField(default=b' ', max_length=4096)),
                ('year', models.CharField(default=b' ', max_length=4096, blank=True)),
                ('title', models.CharField(default=b' ', max_length=4096)),
                ('city', models.CharField(default=b' ', max_length=4096)),
                ('indb', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['isbn'],
            },
        ),
        migrations.CreateModel(
            name='RepositoryFailedIsbn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn10', models.CharField(max_length=4096)),
                ('isbn13', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ['isbn10'],
            },
        ),
        migrations.CreateModel(
            name='TextsCdrom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('books', models.ManyToManyField(to='bibliography.Book', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimePoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.CharField(max_length=1024)),
                ('modifier', models.ForeignKey(default=0, blank=True, to='bibliography.DateModifier')),
                ('system', models.ForeignKey(default=0, blank=True, to='bibliography.DateSystem')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSpan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4096, blank=True)),
                ('begin', models.ForeignKey(related_name='begin_set', to='bibliography.TimePoint')),
                ('end', models.ForeignKey(related_name='end_set', to='bibliography.TimePoint')),
            ],
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256, db_index=True)),
                ('publication', models.ForeignKey(to='bibliography.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='VolumeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.SlugField(unique=True)),
                ('description', models.CharField(max_length=1024)),
                ('read_as', models.CharField(default=b'', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ArticleAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.CreateModel(
            name='BookAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.AddField(
            model_name='repositorycacheauthor',
            name='book',
            field=models.ForeignKey(to='bibliography.RepositoryCacheBook'),
        ),
        migrations.AddField(
            model_name='publisheraddress',
            name='state',
            field=models.ForeignKey(to='bibliography.PublisherState'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='addresses',
            field=models.ManyToManyField(to='bibliography.PublisherAddress', through='bibliography.PublisherAddressPublisherRelation', blank=True),
        ),
        migrations.AddField(
            model_name='publisher',
            name='isbns',
            field=models.ManyToManyField(to='bibliography.PublisherIsbn', blank=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='publisher',
            field=models.ForeignKey(to='bibliography.Publisher'),
        ),
        migrations.AddField(
            model_name='publication',
            name='volume_type',
            field=models.ForeignKey(to='bibliography.VolumeType'),
        ),
        migrations.AddField(
            model_name='migrpublisherriviste',
            name='publisher',
            field=models.ForeignKey(to='bibliography.Publisher'),
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_type',
            field=models.ForeignKey(to='bibliography.IssueType'),
        ),
        migrations.AddField(
            model_name='issue',
            name='volume',
            field=models.ForeignKey(to='bibliography.Volume'),
        ),
        migrations.AddField(
            model_name='categorytimespanrelation',
            name='time_span',
            field=models.ForeignKey(to='bibliography.TimeSpan'),
        ),
        migrations.AddField(
            model_name='booktimespanrelation',
            name='time_span',
            field=models.ForeignKey(to='bibliography.TimeSpan'),
        ),
        migrations.AddField(
            model_name='bookseriewithoutisbn',
            name='publisher',
            field=models.ForeignKey(to='bibliography.Publisher'),
        ),
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(to='bibliography.Category', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(to='bibliography.Publisher'),
        ),
        migrations.AddField(
            model_name='authorrelation',
            name='author',
            field=models.ForeignKey(to='bibliography.Author'),
        ),
        migrations.AddField(
            model_name='authorrelation',
            name='author_role',
            field=models.ForeignKey(to='bibliography.AuthorRole'),
        ),
        migrations.AddField(
            model_name='authorrelation',
            name='content_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='authornamerelation',
            name='name_type',
            field=models.ForeignKey(to='bibliography.NameType'),
        ),
        migrations.AddField(
            model_name='author',
            name='cache',
            field=models.OneToOneField(null=True, editable=False, to='bibliography.AuthorCache'),
        ),
        migrations.AddField(
            model_name='author',
            name='format_collection',
            field=models.ForeignKey(to='bibliography.NameFormatCollection'),
        ),
        migrations.AddField(
            model_name='author',
            name='names',
            field=models.ManyToManyField(to='bibliography.NameType', through='bibliography.AuthorNameRelation', blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='issue',
            field=models.ForeignKey(to='bibliography.Issue'),
        ),
        migrations.AddField(
            model_name='bookauthorrelation',
            name='book',
            field=models.ForeignKey(to='bibliography.Book'),
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author', through='bibliography.BookAuthorRelation', blank=True),
        ),
        migrations.AddField(
            model_name='articleauthorrelation',
            name='article',
            field=models.ForeignKey(to='bibliography.Article'),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author', through='bibliography.ArticleAuthorRelation', blank=True),
        ),
    ]
