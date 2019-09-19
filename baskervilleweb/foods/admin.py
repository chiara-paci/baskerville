from django.contrib import admin

# Register your models here.

from . import models

# from foods.models import Vendor,MicroNutrient,MicroNutrientClass,Product,ProductMicroNutrient,MeasureUnit,FoodDiaryEntry,WeightDiaryEntry
# from foods.models import ProductCategory
# from foods.models import UsdaNndFoodGroup,UsdaNndFood,UsdaNndLangual,UsdaNndFoodLangualRelation
# from foods.models import Recipe,RecipeProduct,FrequentDiaryEntry

admin.site.register(models.Vendor)
admin.site.register(models.MicroNutrientClass)
admin.site.register(models.UsdaNndFoodGroup)
admin.site.register(models.UsdaNndLangual)
admin.site.register(models.UsdaNndFoodLangualRelation)

class ProductInline(admin.TabularInline):
    model = models.Product
    extra = 0

class ProductMicroNutrientInline(admin.TabularInline):
    model = models.ProductMicroNutrient
    extra = 0
    
class FrequentDiaryEntryAdmin(admin.ModelAdmin):
    list_display = [ "product","quantity","measure_unit" ]

admin.site.register(models.FrequentDiaryEntry,FrequentDiaryEntryAdmin)

class ProductCategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

admin.site.register(models.ProductCategory,ProductCategoryAdmin)

class UsdaNndFoodAdmin(admin.ModelAdmin):
    list_display=["short_description","common_name","manufacturer_name","food_group","scientific_name"]

admin.site.register(models.UsdaNndFood,UsdaNndFoodAdmin)

class MicroNutrientAdmin(admin.ModelAdmin):
    list_display = [ 'name','rda','rda_max','nutrient_class' ]
    list_editable = ["rda","rda_max",'nutrient_class' ]
    list_filter = [ 'nutrient_class' ]
    inlines = [ProductMicroNutrientInline]

admin.site.register(models.MicroNutrient,MicroNutrientAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = [ 'name','vendor','category','value_for','high_processed','kcal','potassium',
                     'sodium','fat','saturated_fat','carbohydrate','sugar','added_sugar',
                     'protein','alcohol','sodium','fiber']
    list_editable = ['category','potassium','sodium','high_processed']
    inlines = [ProductMicroNutrientInline]
    exclude = [ 'micro_nutrients' ]
    list_filter = [ 'vendor','category' ]

admin.site.register(models.Product,ProductAdmin)

class ProductMicroNutrientAdmin(admin.ModelAdmin):
    list_display = [ 'product','micro_nutrient','quantity' ]
    list_filter = [ 'product','micro_nutrient' ]

admin.site.register(models.ProductMicroNutrient,ProductMicroNutrientAdmin)

class MeasureUnitAdmin(admin.ModelAdmin):
    list_display = [ 'name','base','factor' ]

admin.site.register(models.MeasureUnit,MeasureUnitAdmin)

class FoodDiaryEntryAdmin(admin.ModelAdmin):
    list_display = [ 'user','time','future','product','quantity','measure_unit',
                     'quantity_real','measure_unit_real',
                     'kcal','fat','saturated_fat','carbohydrate','sugar','protein']
    list_filter = [ 'user','product' ]
    list_editable = [ 'future','time' ]
    date_hierarchy = 'time'
    ordering = [ '-time' ]

admin.site.register(models.FoodDiaryEntry,FoodDiaryEntryAdmin)

class WeightDiaryEntryAdmin(admin.ModelAdmin):
    list_display = [ 'user','time','weight','need','base' ]

admin.site.register(models.WeightDiaryEntry,WeightDiaryEntryAdmin)

class RecipeProductInline(admin.TabularInline):
    model = models.RecipeProduct
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = [ 'name','time','final_weight','total_weight' ]
    inlines = [RecipeProductInline]

admin.site.register(models.Recipe,RecipeAdmin)

class RecipeProductAdmin(admin.ModelAdmin):
    list_display = [ 'recipe','product','quantity','measure_unit' ]
    list_filter = [ 'recipe','product']

admin.site.register(models.RecipeProduct,RecipeProductAdmin)
