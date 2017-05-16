from django.contrib import admin

# Register your models here.

from . import models

class PhotoMetaDatumInline(admin.TabularInline):
    model = models.PhotoMetaDatum
    extra = 0

class PhotoMetaDatumAdmin(admin.ModelAdmin):
    list_display=["photo","label","value"]

admin.site.register(models.PhotoMetaDatum,PhotoMetaDatumAdmin)

class ImageFormatAdmin(admin.ModelAdmin):
    list_display=["name","description"]

admin.site.register(models.ImageFormat,ImageFormatAdmin)

class PhotoAdmin(admin.ModelAdmin):
    list_display=["full_path","mimetype","format","width","height","mode"]
    inlines=(PhotoMetaDatumInline,)

admin.site.register(models.Photo,PhotoAdmin)

class MetaLabelAdmin(admin.ModelAdmin):
    inlines=(PhotoMetaDatumInline,)

admin.site.register(models.MetaLabel,MetaLabelAdmin)

