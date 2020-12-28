from django.contrib import admin
from django.contrib.contenttypes import admin as ctadmin

# Register your models here.

from . import models

admin.site.register(models.ContainerType)

class ObjectContainerRelationAdmin(admin.ModelAdmin):
    save_as=True

admin.site.register(models.ObjectContainerRelation,ObjectContainerRelationAdmin)

class ObjectContainerRelationInline(admin.TabularInline):
    model = models.ObjectContainerRelation
    extra = 0

class ContainerAdmin(admin.ModelAdmin):
    list_display = [ "label", "type", "description" ]
    inlines = [ObjectContainerRelationInline]
    save_as = True

admin.site.register(models.Container,ContainerAdmin)




