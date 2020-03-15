from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Tool)
admin.site.register(models.FoodCategory)
admin.site.register(models.RecipeCategory)
admin.site.register(models.StepToolRelation)

admin.site.register(models.Retailer)
admin.site.register(models.Vendor)

#admin.site.register(models.IngredientToolRelation)

class IngredientInline(admin.TabularInline):
    model = models.Ingredient
    extra = 0

class ProductInline(admin.TabularInline):
    model = models.Product
    extra = 0

class StepInline(admin.TabularInline):
    model = models.Step
    extra = 0

class StepToolInline(admin.TabularInline):
    model = models.StepToolRelation
    #readonly_fields = [ "tool", "step" ] #"recipe", "step" ]
    #can_delete = False
    extra = 0

    #def has_add_permission(self,request, obj): return False

class RecipeIngredientGroupRelationInline(admin.TabularInline):
    model = models.RecipeIngredientGroupRelation
    extra = 0

class RecipeIngredientAlternativeRelationInline(admin.TabularInline):
    model = models.RecipeIngredientAlternativeRelation
    extra = 0

class IngredientAlternativeGroupRelationInline(admin.TabularInline):
    model = models.IngredientAlternativeGroupRelation
    extra = 0

class RecipeRecipeSetRelationInline(admin.TabularInline):
    model = models.RecipeRecipeSetRelation
    extra = 0


############

class StepSequenceAdmin(admin.ModelAdmin):
    inlines=[StepInline]

admin.site.register(models.StepSequence,StepSequenceAdmin)

class StepAdmin(admin.ModelAdmin):
    list_display=["sequence","pos","description"]
    list_editable=["pos"]
    inlines=[StepToolInline]
    list_filter=["sequence"]

admin.site.register(models.Step,StepAdmin)

class RecipeAdmin(admin.ModelAdmin):
    #inlines=[IngredientInline] #,StepToolInline,IngredientToolInline]
    list_display=["name","serving","category"] #,"ingredients"]
    inlines=[RecipeIngredientGroupRelationInline,
             RecipeIngredientAlternativeRelationInline,
             RecipeRecipeSetRelationInline]

admin.site.register(models.Recipe,RecipeAdmin)

class MeasureUnitAdmin(admin.ModelAdmin):
    list_display=["name","apply_to","base","factor"]

admin.site.register(models.MeasureUnit,MeasureUnitAdmin)

class FoodAdmin(admin.ModelAdmin):
    list_display=["name","category"]
    inline=[ProductInline,IngredientInline]

admin.site.register(models.Food,FoodAdmin)

class RetailerInline(admin.TabularInline):
    model = models.Product.retailers.through
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    list_display=["name","food","vendor"]
    inlines=[RetailerInline]

admin.site.register(models.Product,ProductAdmin)

class IngredientAdmin(admin.ModelAdmin):
    list_display=["food","quantity","measure"]

admin.site.register(models.Ingredient,IngredientAdmin)

class IngredientGroupAdmin(admin.ModelAdmin):
    inlines=[RecipeIngredientGroupRelationInline,
             IngredientAlternativeGroupRelationInline]

admin.site.register(models.IngredientGroup,IngredientGroupAdmin)

class IngredientAlternativeAdmin(admin.ModelAdmin):
    inlines=[RecipeIngredientAlternativeRelationInline,
             IngredientAlternativeGroupRelationInline]

admin.site.register(models.IngredientAlternative,IngredientAlternativeAdmin)

class RecipeSetAdmin(admin.ModelAdmin):
    inlines=[RecipeRecipeSetRelationInline]

admin.site.register(models.RecipeSet,RecipeSetAdmin)

class RecipeLabelAdmin(admin.ModelAdmin):
    inlines=[RecipeRecipeSetRelationInline]

admin.site.register(models.RecipeLabel,RecipeLabelAdmin)

admin.site.register(models.RecipeIngredientGroupRelation)
admin.site.register(models.RecipeIngredientAlternativeRelation)
admin.site.register(models.IngredientAlternativeGroupRelation)
admin.site.register(models.RecipeRecipeSetRelation)
