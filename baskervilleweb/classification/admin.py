from django.contrib import admin

# Register your models here.

from classification.models import Argument,ArgumentSuffix,ArgumentSuffixCollection,ArgumentSelector
from classification.models import ArgumentClassification
from classification.models import LanguageAuxiliaryNumber
from classification.models import LanguageNumber
from classification.models import LanguageClassification
from classification.models import PlaceAuxiliaryNumber
from classification.models import PlaceNumber
from classification.models import PlaceClassification
from classification.models import TimeClassification
from classification.models import FormClassification
from classification.models import ShortClassificationManager
from classification.models import ShortClassification
from classification.models import Classification

admin.site.register(LanguageAuxiliaryNumber)
admin.site.register(LanguageNumber)
admin.site.register(LanguageClassification)
admin.site.register(PlaceAuxiliaryNumber)
admin.site.register(PlaceNumber)
admin.site.register(PlaceClassification)
admin.site.register(TimeClassification)
admin.site.register(FormClassification)
admin.site.register(ShortClassification)
admin.site.register(Classification)

class RootArgumentFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'category'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        qset = model_admin.get_queryset(request)
        t=[]
        for arg in qset.filter(parent__id=0):
            if arg.id==0: continue
            t.append( (arg.number,str(arg)) )
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        return queryset.filter(identifier__istartswith=self.value())

class ArgumentAdmin(admin.ModelAdmin):
    list_display=["identifier","name","parent_identifier","number"]
    list_editable=["number","name"]
    list_display_links=["identifier"]
    save_as=True
    list_filter=[ RootArgumentFilter ]


admin.site.register(ArgumentSelector)
admin.site.register(Argument,ArgumentAdmin)

class ArgumentSuffixAdmin(admin.ModelAdmin):
    list_display=["collection","identifier","name","parent_identifier","number"]
    list_editable=["number"]
    list_display_links=["name"]
    save_as=True
    list_filter=[ "collection" ]

admin.site.register(ArgumentSuffix,ArgumentSuffixAdmin)

class ArgumentSelectorInline(admin.TabularInline):
    model = ArgumentSelector
    extra = 0

class ArgumentSuffixInline(admin.TabularInline):
    model = ArgumentSuffix
    extra = 0

class ArgumentSuffixCollectionAdmin(admin.ModelAdmin):
    list_display=["name","number","phase","description","roots"]
    list_editable=["number"]
    inlines=[ArgumentSelectorInline,ArgumentSuffixInline]

admin.site.register(ArgumentSuffixCollection,ArgumentSuffixCollectionAdmin)

class RootArgumentClassificationFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'category'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        qset = Argument.objects.all()
        t=[]
        for arg in qset.filter(parent__id=0):
            if arg.id==0: continue
            t.append( (arg.number,str(arg)) )
        return tuple(t)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if not self.value(): return queryset
        return queryset.filter(number__istartswith=self.value())

class ArgumentClassificationAdmin(admin.ModelAdmin):
    list_display=["number","name"]
    save_as=True
    list_filter=[ RootArgumentClassificationFilter ]

admin.site.register(ArgumentClassification,ArgumentClassificationAdmin)
