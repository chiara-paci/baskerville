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
admin.site.register(models.ExecutionToolRelation)
admin.site.register(models.IngredientToolRelation)

class IngredientInline(admin.TabularInline):
    model = models.Ingredient
    extra = 0

class StepInline(admin.TabularInline):
    model = models.Step
    extra = 0


class ExecutionToolInline(admin.TabularInline):
    model = models.ExecutionToolRelation
    readonly_fields = [ "tool", "step" ] #"recipe", "step" ]
    can_delete = False
    extra = 0

    def has_add_permission(self,request, obj): return False

class IngredientToolInline(admin.TabularInline):
    model = models.IngredientToolRelation
    readonly_fields = [ "tool", "ingredient", "step" ]#, "recipe" ]
    can_delete = False
    extra = 0

    def has_add_permission(self,request, obj): return False

class RecipeAdmin(admin.ModelAdmin):
    inlines=[IngredientInline] #,ExecutionToolInline,IngredientToolInline]
    list_display=["name","ingredients"]

admin.site.register(models.Recipe,RecipeAdmin)

class StepSequenceAdmin(admin.ModelAdmin):
    inlines=[StepInline]

admin.site.register(models.StepSequence,StepSequenceAdmin)
