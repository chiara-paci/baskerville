from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.ContainerType)

class ContainerAdmin(admin.ModelAdmin):
    list_display = [ "label", "type", "description" ]

admin.site.register(models.Container,ContainerAdmin)

admin.site.register(models.ObjectContainerRelation)
