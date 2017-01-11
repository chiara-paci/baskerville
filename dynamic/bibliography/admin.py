from django.contrib import admin
from django.conf.urls import include, url
from django import forms

# Register your models here.

from bibliography.models import Person,CategoryPersonRelation

from bibliography.models import NameFormat,NameType,Author,PersonNameRelation,MigrAuthor,NameFormatCollection,PersonCache
from bibliography.models import PublisherIsbn,Publisher,PublisherAddress,PublisherAddressPublisherRelation,MigrPublisherRiviste,PublisherState
from bibliography.models import VolumeType,Publication,Volume,IssueType,Issue
from bibliography.models import Category,CategoryRelation,BookSerieWithoutIsbn,CategoryTreeNode
from bibliography.models import Book,AuthorRole,BookAuthorRelation,TextsCdrom
from bibliography.models import Article,ArticleAuthorRelation,AuthorRelation
from bibliography.models import RepositoryCacheBook,RepositoryCacheAuthor,RepositoryFailedIsbn

from bibliography.models import DateModifier,TimePoint,TimeSpan,CategoryTimeSpanRelation #,BookTimeSpanRelation

from bibliography.models import PlaceType,Place,AlternatePlaceName,PlaceRelation,CategoryPlaceRelation

from bibliography.models import Language,LanguageFamily,LanguageFamilyRelation,LanguageFamilyFamilyRelation
from bibliography.models import LanguageVarietyType,LanguageVariety,CategoryLanguageRelation


class DateModifierAdmin(admin.ModelAdmin):
    list_display=[ "anchor","name","pos","reverse" ]
    list_editable=["name","pos","reverse"]

    def anchor(self,obj):
        U=unicode(obj).strip()
        if U: return U
        return "[default]"

admin.site.register(DateModifier,DateModifierAdmin)

class TimePointAdmin(admin.ModelAdmin):
    list_display=["date","modifier","time_spans","begins","ends"]

admin.site.register(TimePoint,TimePointAdmin)

admin.site.register(CategoryTimeSpanRelation)
admin.site.register(CategoryPlaceRelation)
admin.site.register(CategoryPersonRelation)
admin.site.register(CategoryLanguageRelation)

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

### language

admin.site.register(LanguageFamilyRelation)
admin.site.register(LanguageFamilyFamilyRelation)
admin.site.register(LanguageVarietyType)

class LanguageFamilyInline(admin.TabularInline):
    model = LanguageFamilyRelation
    extra = 0

class LanguageVarietyInline(admin.TabularInline):
    model = LanguageVariety
    extra = 0

class LanguageAdmin(admin.ModelAdmin):
    list_display=[ "__unicode__","name","families","varieties" ]
    list_editable=[ "name" ]
    inlines = [LanguageFamilyInline,LanguageVarietyInline]

admin.site.register(Language,LanguageAdmin)

class LanguageFamilyChildrenInline(admin.TabularInline):
    model = LanguageFamilyFamilyRelation
    extra = 0
    fk_name = "parent"
    verbose_name = "child"
    verbose_name_plural = "children"

class LanguageFamilyParentsInline(admin.TabularInline):
    model = LanguageFamilyFamilyRelation
    extra = 0
    fk_name = "child"
    verbose_name = "parent"
    verbose_name_plural = "parents"

class LanguageFamilyAdmin(admin.ModelAdmin):
    list_display=[ "__unicode__","name","parents","children","languages" ]
    list_editable=[ "name" ]
    inlines = [LanguageFamilyInline,LanguageFamilyChildrenInline,LanguageFamilyParentsInline]

admin.site.register(LanguageFamily,LanguageFamilyAdmin)

class LanguageVarietyAdmin(admin.ModelAdmin):
    list_display=[ "__unicode__","name","type","language" ]
    list_editable=[ "name" ]

admin.site.register(LanguageVariety,LanguageVarietyAdmin)

### place

class PlaceTypeAdmin(admin.ModelAdmin):
    list_display=["__unicode__","name"]
    list_editable=["name"]


admin.site.register(PlaceType,PlaceTypeAdmin)
admin.site.register(PlaceRelation)
admin.site.register(AlternatePlaceName)

class PlacePlacesInline(admin.TabularInline):
    model = PlaceRelation
    extra = 0
    fk_name = "area"
    verbose_name = "place"
    verbose_name_plural = "places"

class PlaceAreasInline(admin.TabularInline):
    model = PlaceRelation
    extra = 0
    fk_name = "place"
    verbose_name = "area"
    verbose_name_plural = "areas"

class AlternatePlaceNameInline(admin.TabularInline):
    model = AlternatePlaceName
    extra = 0

class PlaceAdmin(admin.ModelAdmin):
    inlines=[AlternatePlaceNameInline,PlacePlacesInline,PlaceAreasInline]

    list_display=["__unicode__","name","type","areas","places","alternate_names" ]
    list_editable=["name"]
    list_filter=["type"]

admin.site.register(Place,PlaceAdmin)


### category
class BookCategoryInline(admin.TabularInline):
    model = Book.categories.through
    extra = 0

class CategoryParentsInline(admin.TabularInline):
    model = CategoryRelation
    extra = 0
    fk_name = "child"
    verbose_name = "parent"
    verbose_name_plural = "parents"

class CategoryChildrenInline(admin.TabularInline):
    model = CategoryRelation
    extra = 0
    fk_name = "parent"
    verbose_name = "child"
    verbose_name_plural = "children"

class CategoryTimeSpanRelationInline(admin.TabularInline):
    model = CategoryTimeSpanRelation
    extra = 0
    verbose_name = "time span"
    verbose_name_plural = "time spans"

class TimeSpanAdmin(admin.ModelAdmin):
    list_display=["__unicode__","begin","end","categories"]
    inlines=[CategoryTimeSpanRelationInline]

admin.site.register(TimeSpan,TimeSpanAdmin)

class CategoryPlaceRelationInline(admin.TabularInline):
    model = CategoryPlaceRelation
    extra = 0
    verbose_name = "place"
    verbose_name_plural = "places"

class CategoryPersonRelationInline(admin.TabularInline):
    model = CategoryPersonRelation
    extra = 0
    verbose_name = "person"
    verbose_name_plural = "people"

class CategoryLanguageRelationInline(admin.TabularInline):
    model = CategoryLanguageRelation
    extra = 0
    verbose_name = "language"
    verbose_name_plural = "languages"

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
        return Category.objects.query_set_branch(queryset,self.value())
        # print type(queryset)
        # return queryset.all().all_in_branch(self.value())

class CategoryTreeRootFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'root'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category_root'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        cat_ids=CategoryTreeNode.objects.until_level(0).values("object_id").distinct()

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
        return Category.objects.query_set_branch(queryset,self.value())
        # print type(queryset)
        # return queryset.all().all_in_branch(self.value())

class CategoryAdmin(admin.ModelAdmin):
    inlines=[CategoryTimeSpanRelationInline,CategoryPlaceRelationInline,CategoryLanguageRelationInline,
             CategoryPersonRelationInline,
             CategoryParentsInline,CategoryChildrenInline,BookCategoryInline]
    list_display=["__unicode__","name","num_books","parents","children","time_span","place","language","person"]
    list_editable=["name"]
    list_filter=[ AlphabeticFilter, CategoryTreeRootFilter, CategoryTreeFilter ]
    fields = ("name","x_tree_nodes","min_level","num_objects","my_branch_depth","my_branch_id")
    readonly_fields = ("x_tree_nodes","min_level","num_objects","my_branch_depth","my_branch_id")
    actions=["merge_categories"]

    def x_tree_nodes(self,instance): 
        ret="<ul>"
        for node in instance.tree_nodes.all():
            ret+="<li>"+str(node)+"</li>"
        ret+="</ul>"
        return ret
    x_tree_nodes.allow_tags=True
    x_tree_nodes.short_description = "tree nodes"

    def merge_categories(self,request,queryset):
        Category.objects.merge(queryset)
    merge_categories.short_description="Merge selected categories"

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
    list_filter=["parent","child"]
    list_display=["__unicode__","parent","child"]
    list_editable=["parent"]

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
admin.site.register(PersonNameRelation)

class AuthorRelationAdmin(admin.ModelAdmin):
    list_display=["year","author","author_role","content_type"]
    list_filter=["year"]

admin.site.register(AuthorRelation,AuthorRelationAdmin)

class NameFormatAdmin(admin.ModelAdmin):
    list_display= ['label','pattern','description']
    list_editable = ['pattern']
    save_as=True

admin.site.register(NameFormat,NameFormatAdmin)

class NameFormatCollectionAdmin(admin.ModelAdmin):
    list_display= ['label','description','preferred','long_format','short_format','list_format','ordering_format']
    list_editable = ['preferred','long_format','short_format','list_format','ordering_format']
    save_as=True

admin.site.register(NameFormatCollection,NameFormatCollectionAdmin)

class AuthorNameInline(admin.TabularInline):
    model = PersonNameRelation
    extra = 0

class MigrAuthorInline(admin.TabularInline):
    model = MigrAuthor
    extra = 0

class PersonAlphabeticFilter(admin.SimpleListFilter):
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

        qset = PersonCache.objects.all()
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

class PersonAdmin(admin.ModelAdmin):
    list_display= ['long_name','short_name','list_name','ordering_name']
    list_filter=[ PersonAlphabeticFilter ]
    inlines=(AuthorNameInline,)

admin.site.register(Person,PersonAdmin)
admin.site.register(PersonCache)

class AuthorAdmin(admin.ModelAdmin):
    inlines=(AuthorNameInline,MigrAuthorInline,BookAuthorRelationInline,ArticleAuthorRelationInline)
    list_display= ['long_name','short_name','list_name','ordering_name']
    list_filter=[ PersonAlphabeticFilter ]

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
    list_display=['issn','issn_crc','title','publisher','volume_type','date_format']
    list_editable=['date_format']

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

