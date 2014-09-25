from django.contrib import admin
from django.conf.urls import patterns, include, url
from django import forms

# Register your models here.

from bibliography.models import NameFormat,NameType,Author,AuthorNameRelation,MigrAuthor,NameFormatCollection,AuthorCache
from bibliography.models import PublisherIsbn,Publisher,PublisherAddress,PublisherAddressPublisherRelation,MigrPublisherRiviste,PublisherState
from bibliography.models import VolumeType,Publication,Volume,IssueType,Issue
from bibliography.models import Category,CategoryRelation,BookSerieWithoutIsbn,CategoryTreeNode
from bibliography.models import Book,AuthorRole,BookAuthorRelation,TextsCdrom
from bibliography.models import Article,ArticleAuthorRelation,AuthorRelation
from bibliography.models import RepositoryCacheBook,RepositoryCacheAuthor,RepositoryFailedIsbn

from bibliography.models import DateSystem,DateModifier,TimePoint,TimeSpan,CategoryTimeSpanRelation,BookTimeSpanRelation

admin.site.register(DateSystem)
admin.site.register(DateModifier)
admin.site.register(TimePoint)
admin.site.register(TimeSpan)
admin.site.register(CategoryTimeSpanRelation)
admin.site.register(BookTimeSpanRelation)

class BookSerieWithoutIsbnAdmin(admin.ModelAdmin):
    list_display=["isbn_ced","isbn_book_prefix","title","title_prefix","publisher"]

admin.site.register(BookSerieWithoutIsbn,BookSerieWithoutIsbnAdmin)

class RepositoryFailedIsbnAdmin(admin.ModelAdmin):
    list_display=["isbn10","isbn13"]

admin.site.register(RepositoryFailedIsbn,RepositoryFailedIsbnAdmin)

class RepositoryCacheAuthorInline(admin.TabularInline):
    model = RepositoryCacheAuthor
    extra = 0

class RepositoryCacheBookForm(forms.ModelForm):
    class Meta:
        widgets = {
            'title': forms.TextInput(attrs={'size': 80}),
            'year': forms.TextInput(attrs={'size': 10}),
        }

class RepositoryCacheBookAdmin(admin.ModelAdmin):
    list_display=["isbn","title","year","indb"]
    list_editable=["title","year"]
    list_filter=["indb","year"]
    inlines = [RepositoryCacheAuthorInline]

    def get_changelist_form(self, request, **kwargs):
        return RepositoryCacheBookForm

admin.site.register(RepositoryCacheBook,RepositoryCacheBookAdmin)

class RepositoryCacheAuthorAdmin(admin.ModelAdmin):
    list_display=["__unicode__","name"]
    list_editable=["name"]

admin.site.register(RepositoryCacheAuthor,RepositoryCacheAuthorAdmin)

### category
class BookCategoryInline(admin.TabularInline):
    model = Book.categories.through
    extra = 0

class CategoryFathersInline(admin.TabularInline):
    model = CategoryRelation
    extra = 0
    fk_name = "child"

class CategoryChildrenInline(admin.TabularInline):
    model = CategoryRelation
    extra = 0
    fk_name = "father"

class AlphabeticFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'initial'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'initial'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        qset = model_admin.get_queryset(request)
        L=qset.extra(select={"initial": "lower(substr(name,1,1))"},order_by=["initial"]).values("initial").distinct()
        t=[]
        for ch in map(lambda x: x["initial"],L):
            t.append( (ch,ch) )
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        return queryset.filter(name__istartswith=self.value())


class CategoryTreeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'branch'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category_branch'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        cat_ids=CategoryTreeNode.objects.until_level(2).values("object_id").distinct()

        qset = model_admin.get_queryset(request).filter(id__in=cat_ids)
        t=map(lambda x: (x.id,x.name),list(qset))
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        print type(queryset)
        return queryset.all().all_in_branch(self.value())

class CategoryAdmin(admin.ModelAdmin):
    inlines=[CategoryFathersInline,CategoryChildrenInline,BookCategoryInline]
    list_display=["__unicode__","name","fathers","children"]
    list_editable=["name"]
    list_filter=[ AlphabeticFilter, CategoryTreeFilter ]

    # def get_urls(self):
    #     urls = super(CategoryAdmin, self).get_urls()
    #     my_urls = [
    #         url(r'^my_view/$', self.admin_site.admin_view(self.my_view), name="my_view"),
    #     ]
    #     return my_urls + urls

    # def my_view(self, request):
    #     # custom view which should return an HttpResponse
    #     pass

admin.site.register(Category,CategoryAdmin)

class CategoryRelationAdmin(admin.ModelAdmin):
    list_filter=["father","child"]
    list_display=["__unicode__","father","child"]
    list_editable=["father"]

admin.site.register(CategoryRelation,CategoryRelationAdmin)

class AlphabeticNodeidFilter(AlphabeticFilter):
    title = 'initial'
    parameter_name = 'initial'

    def lookups(self, request, model_admin):
        qset = model_admin.get_queryset(request)
        L=qset.extra(select={"initial": "lower(substr(node_id,1,1))"},order_by=["initial"]).values("initial").distinct()
        t=[]
        for ch in map(lambda x: x["initial"],L):
            t.append( (ch,ch) )
        return tuple(t)

    def queryset(self, request, queryset):
        if not self.value(): return queryset
        return queryset.filter(node_id__istartswith=self.value())


class CategoryTreeNodeAdmin(admin.ModelAdmin):
    list_display=["node_id","level","num_objects","content_object","has_children"]
    list_filter=[ AlphabeticNodeidFilter,"level","is_category" ]

admin.site.register(CategoryTreeNode,CategoryTreeNodeAdmin)

### author

class BookAuthorRelationInline(admin.TabularInline):
    model = BookAuthorRelation
    extra = 0
    
class ArticleAuthorRelationInline(admin.TabularInline):
    model = ArticleAuthorRelation
    extra = 0
    
admin.site.register(NameType)
admin.site.register(AuthorNameRelation)

class AuthorRelationAdmin(admin.ModelAdmin):
    list_display=["year","author","author_role","content_type"]
    list_filter=["year"]

admin.site.register(AuthorRelation,AuthorRelationAdmin)

class NameFormatAdmin(admin.ModelAdmin):
    list_display= ['label','pattern','description']
    list_editable = ['pattern']

admin.site.register(NameFormat,NameFormatAdmin)

class NameFormatCollectionAdmin(admin.ModelAdmin):
    list_display= ['label','description','long_format','short_format','list_format','ordering_format']
    list_editable = ['long_format','short_format','list_format','ordering_format']

admin.site.register(NameFormatCollection,NameFormatCollectionAdmin)

class AuthorNameInline(admin.TabularInline):
    model = AuthorNameRelation
    extra = 0

class MigrAuthorInline(admin.TabularInline):
    model = MigrAuthor
    extra = 0


class AuthorAlphabeticFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'initial'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'initial'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        qset = AuthorCache.objects.all()
        L=qset.extra(select={"initial": "lower(substr(list_name,1,1))"},order_by=["initial"]).values("initial").distinct()
        t=[]
        for ch in map(lambda x: x["initial"],L):
            t.append( (ch,ch) )
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        return queryset.filter(cache__list_name__istartswith=self.value())

class AuthorAdmin(admin.ModelAdmin):
    inlines=(AuthorNameInline,MigrAuthorInline,BookAuthorRelationInline,ArticleAuthorRelationInline)
    list_display= ['long_name','short_name','list_name','ordering_name']
    list_filter=[ AuthorAlphabeticFilter ]

admin.site.register(Author,AuthorAdmin)

class MigrAuthorAdmin(admin.ModelAdmin):
    list_display= ['cod','ind','author']

admin.site.register(MigrAuthor,MigrAuthorAdmin)

### publisher

class PublisherAddressAdmin(admin.ModelAdmin):
    list_display=["city","state"]
    list_filter=["state"]

admin.site.register(PublisherAddress,PublisherAddressAdmin)

class PublisherAddressInline(admin.TabularInline):
    model = PublisherAddress
    extra = 0

class PublisherStateAdmin(admin.ModelAdmin):
    inlines=(PublisherAddressInline,)

admin.site.register(PublisherState,PublisherStateAdmin)
admin.site.register(PublisherAddressPublisherRelation)
admin.site.register(MigrPublisherRiviste)

class PublisherAddressPublisherInline(admin.TabularInline):
    model = PublisherAddressPublisherRelation
    extra = 0

class PublisherIsbnInline(admin.TabularInline):
    model = Publisher.isbns.through
    extra = 0

class MigrPublisherRivisteInline(admin.TabularInline):
    model = MigrPublisherRiviste
    extra = 0

class PublisherAdmin(admin.ModelAdmin):
    inlines=(PublisherAddressPublisherInline,PublisherIsbnInline,MigrPublisherRivisteInline)
    list_display=["name","address","isbn_prefix","alias"]
    list_editable=["alias"]
    exclude = [ 'isbns' ]

admin.site.register(Publisher,PublisherAdmin)

class PublisherIsbnAdmin(admin.ModelAdmin):
    list_display=["preferred","isbn","publishers"]
    list_editable=["isbn"]
    inlines=(PublisherIsbnInline,)

admin.site.register(PublisherIsbn,PublisherIsbnAdmin)


### publication

admin.site.register(VolumeType)
admin.site.register(Volume)
admin.site.register(IssueType)

class PublicationAdmin(admin.ModelAdmin):
    list_display=['issn','issn_crc','title','publisher','volume_type']

admin.site.register(Publication,PublicationAdmin)

class IssueAdmin(admin.ModelAdmin):
    list_display=['issn','issn_num','title']
    save_as=True

admin.site.register(Issue,IssueAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display=["title","get_authors","issue","issn","issn_num","page_begin","page_end"]
    inlines=[ArticleAuthorRelationInline]
    exclude = ["authors"]

admin.site.register(Article,ArticleAdmin)

class ArticleAuthorRelationAdmin(admin.ModelAdmin):
    list_display=["author","article","author_role","pos"]
    list_editable=["author_role"]

admin.site.register(ArticleAuthorRelation,ArticleAuthorRelationAdmin)

### books

class BookAlphabeticFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'initial'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'initial'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        qset = model_admin.get_queryset(request)
        L=qset.extra(select={"initial": "lower(substr(title,1,1))"},order_by=["initial"]).values("initial").distinct()
        t=[]
        for ch in map(lambda x: x["initial"],L):
            t.append( (ch,ch) )
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        return queryset.filter(title__istartswith=self.value())


class BookAdmin(admin.ModelAdmin):
    list_display=["isbn_cache10","isbn_cache13","isbn_crc13","get_authors","get_secondary_authors","title","year","publisher"]
    inlines=[BookAuthorRelationInline,BookCategoryInline]
    exclude = ["categories","authors"]
    list_filter=[ BookAlphabeticFilter ]

admin.site.register(Book,BookAdmin)

class AuthorRoleAdmin(admin.ModelAdmin):
    list_display=["label","description","cover_name","action","pos"]
    list_editable=["cover_name","action","pos"]

admin.site.register(AuthorRole,AuthorRoleAdmin)

class BookAuthorRelationAdmin(admin.ModelAdmin):
    list_filter=["author"]

admin.site.register(BookAuthorRelation,BookAuthorRelationAdmin)

class BooksCdromInline(admin.TabularInline):
    model = TextsCdrom.books.through
    extra = 0

class TextsCdromAdmin(admin.ModelAdmin):
    list_display=["label","description"]
    inlines=[BooksCdromInline]
    exclude=["books"]

admin.site.register(TextsCdrom,TextsCdromAdmin)

