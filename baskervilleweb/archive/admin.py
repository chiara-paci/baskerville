from django.contrib import admin

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
    list_display=["photo","label","value"]

admin.site.register(models.ExifDatum,ExifDatumAdmin)

class ImageFormatAdmin(admin.ModelAdmin):
    list_display=["name","description"]

admin.site.register(models.ImageFormat,ImageFormatAdmin)

class AlbumPhotoInline(admin.TabularInline):
    model = models.Album.photos.through
    extra = 0


class PhotoAdmin(admin.ModelAdmin):
    list_display=["full_path","thumbnail","mimetype","format","width","height",
                  "mode","datetime","rotated","mirrored"]
    inlines=(AlbumPhotoInline,PhotoMetaDatumInline,ExifDatumInline,)

    def thumbnail(self,obj):
        return u'<img src="%s" />' % obj.thumb_url()
    thumbnail.short_description = 'Thumbnail'
    thumbnail.allow_tags = True

admin.site.register(models.Photo,PhotoAdmin)

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


class AlbumAdmin(admin.ModelAdmin):
    inlines=(AlbumPhotoInline,)

admin.site.register(models.Album,AlbumAdmin)
