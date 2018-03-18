from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.FoodCategory)
admin.site.register(models.RecipeCategory)
admin.site.register(models.Tool)
admin.site.register(models.Step)
admin.site.register(models.MeasureUnit)
admin.site.register(models.Food)
admin.site.register(models.Ingredient)


class IngredientInline(admin.TabularInline):
    model = models.Ingredient
    extra = 0

class StepInline(admin.TabularInline):
    model = models.Step
    extra = 0

class RecipeAdmin(admin.ModelAdmin):
    inlines=[IngredientInline]
    list_display=["name","ingredients"]

admin.site.register(models.Recipe,RecipeAdmin)

class StepSequenceAdmin(admin.ModelAdmin):
    inlines=[StepInline]

admin.site.register(models.StepSequence,StepSequenceAdmin)
