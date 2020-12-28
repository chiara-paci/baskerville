from django.contrib import admin
import django.forms as forms
from django.shortcuts import render
from django.template import Template, Context , RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

# Register your models here.

from . import models

class PhotoMetaDatumInline(admin.TabularInline):
    model = models.PhotoMetaDatum
    extra = 0

class PhotoMetaDatumAdmin(admin.ModelAdmin):
    list_display=["photo","label","value"]

admin.site.register(models.PhotoMetaDatum,PhotoMetaDatumAdmin)

class ExifDatumInline(admin.TabularInline):
    model = models.ExifDatum
    extra = 0

class ExifDatumAdmin(admin.ModelAdmin):
    list_display=["asset","label","value"]

admin.site.register(models.ExifDatum,ExifDatumAdmin)

class ImageFormatAdmin(admin.ModelAdmin):
    list_display=["name","description"]

admin.site.register(models.ImageFormat,ImageFormatAdmin)

class MetaLabelAdmin(admin.ModelAdmin):
    inlines=(PhotoMetaDatumInline,)

admin.site.register(models.MetaLabel,MetaLabelAdmin)

class ExifLabelAdmin(admin.ModelAdmin):
    list_display=["name","category","type","exif_id"]
    inlines=(ExifDatumInline,)

admin.site.register(models.ExifLabel,ExifLabelAdmin)

class ExifTypeAdmin(admin.ModelAdmin):
    list_display=["name","short","exif_id"]
admin.site.register(models.ExifType,ExifTypeAdmin)

class AlbumAlbumPhotoInline(admin.TabularInline):
    model = models.Album.photos.through
    extra = 0
    fields = ( "photo","thumbnail" )
    readonly_fields = ("thumbnail",)

    def thumbnail(self,obj):
        return mark_safe('<img src="%s" />' % obj.photo.thumb_url())
    thumbnail.short_description = 'Thumbnail'
    #thumbnail.allow_tags = True

class AlbumAdmin(admin.ModelAdmin):
    inlines=(AlbumAlbumPhotoInline,) 
    filter_horizontal=["photos"]
    list_display = [ "name","photos_count" ]
    save_on_top = True

admin.site.register(models.Album,AlbumAdmin)

### Photo

class YearListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('year')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        ret=[ (str(x),str(x)) for x in models.PhotoD.objects.get_years() ]
        return ret

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        val=self.value()
        if not val: return queryset
        val=int(val)
        return queryset.filter(datetime__year=val)

class AlbumListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('album')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'album'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        ret=[ ("0","None") ]
        ret+=[ (str(x.id),str(x)) for x in models.Album.objects.all() ]
        return ret

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        val=self.value()
        if not val: return queryset
        if val=="0":
            albums=[ x.id for x in models.Album.objects.all() ]
            return queryset.exclude(album__id__in=albums)
        val=int(val)
        return queryset.filter(album__id=val)

class PhotoAlbumPhotoInline(admin.TabularInline):
    model = models.Album.photos.through
    extra = 0

class PhotoDAdmin(admin.ModelAdmin):
    list_display=["full_path","albums","thumbnail","mimetype","format","width","height",
                  "mode","datetime","rotated","mirrored"]
    inlines=(PhotoAlbumPhotoInline,PhotoMetaDatumInline) 
    #actions=["add_to_album"]
    #actions_on_bottom = True
    date_hierarchy = "datetime"
    save_on_top = True
    list_filter=[YearListFilter,AlbumListFilter]

    def thumbnail(self,obj):
        return mark_safe('<img src="%s" />' % obj.thumb_url())
    thumbnail.short_description = 'Thumbnail'

    def add_to_album(self,request,queryset):
        class MyForm(forms.Form):
            _selected_action = forms.CharField(widget=forms.MultipleHiddenInput) 
            album = forms.ModelChoiceField(queryset=models.Album.objects.all(),empty_label=None)
        succ_msg='{% load humanize %}{{ count|apnumber}} object{{ count|pluralize }} updated'
        if request.POST and ("post" in request.POST):
            form = MyForm(request.POST)
            if form.is_valid():
                album=form.cleaned_data["album"]
                for obj in queryset:
                    album.photos.add(obj)
                self.message_user(request, Template(succ_msg).render(Context({'count':queryset.count()})))
                return HttpResponseRedirect(request.get_full_path())

        form = MyForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request,'admin/archive/add_to_album.html', 
                      context={'objects': queryset, 'form': form, 'path':request.get_full_path()})
    add_to_album.short_description = 'Add to album'

admin.site.register(models.PhotoD,PhotoDAdmin)

class PhotoAssetAdmin(admin.ModelAdmin):
    list_display=["full_path","thumbnail","mimetype","format","width","height",
                  "mode","datetime","rotated","mirrored"]
    inlines=(ExifDatumInline,)
    actions_on_bottom = True
    date_hierarchy = "photo__datetime"
    save_on_top = True
    list_filter=["mimetype","mode","width","height"]

    def thumbnail(self,obj):
        return mark_safe('<img src="%s" />' % obj.thumb_url())
    thumbnail.short_description = 'Thumbnail'

admin.site.register(models.PhotoAsset,PhotoAssetAdmin)

admin.site.register(models.Document)

class DocumentAssetAdmin(admin.ModelAdmin):
    list_display=["full_path","document","thumbnail","mimetype","datetime"]

    def thumbnail(self,obj):
        return mark_safe('<img src="%s" />' % obj.thumb_url())
    thumbnail.short_description = 'Thumbnail'

admin.site.register(models.DocumentAsset,DocumentAssetAdmin)


admin.site.register(models.DocumentCollection)

class DocumentMetaDatumAdmin(admin.ModelAdmin):
    list_display = [ "document","label","value" ]

admin.site.register(models.DocumentMetaDatum,DocumentMetaDatumAdmin)


class DocumentAssetMetaDatumAdmin(admin.ModelAdmin):
    list_display = [ "document_asset","label","value" ]

admin.site.register(models.DocumentAssetMetaDatum,DocumentAssetMetaDatumAdmin)
