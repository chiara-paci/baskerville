from django.db import models
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError

import datetime

# Create your models here.

class Vendor(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self): return unicode(self.name)

    class Meta:
        ordering = [ 'name' ]

class MicroNutrientClass(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self): return unicode(self.name)

    class Meta:
        ordering = [ 'name' ]

class MicroNutrient(models.Model):
    name = models.CharField(max_length=1024)
    nutrient_class = models.ForeignKey(MicroNutrientClass)
    rda = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='rda (mg)',default=0.0)
    rda_max = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='rda max (mg)',default=0.0)
    

    def __unicode__(self): return unicode(self.name)

    class Meta:
        ordering = [ 'name' ]

# class GlycemicIndex(models.Model):
#     name = models.CharField(max_length=1024)
#     glucose = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True)
#     white_bread = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True)
#     insulin_index = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True)

#     def save(self,*args,**kwargs):
#         if not self.glucose and not self.white_bread:
#             raise ValidationError(_("Or glucose or white bread index must be provided"),
#                                   code="glucose_or_white_bread")
#         if not self.glucose:
#             self.glucose=self.white_bread/1.37
#         if not self.white_bread:
#             self.white_bread=self.glucose*1.37
#         super(GlycemicIndex, self).save(self,*args,**kwargs)

class ProductCategory(models.Model):
    name = models.CharField(max_length=1024)
    
    def __unicode__(self): return unicode(self.name)

class Product(models.Model):
    name = models.CharField(max_length=1024)
    category = models.ForeignKey(ProductCategory)
    vendor = models.ForeignKey(Vendor)
    value_for = models.CharField(max_length=128,default='100 g',choices = ( ( "100 g", "100 g" ),
                                                                            ( "100 ml", "100 ml" ) ))

    high_processed = models.BooleanField(default=False)
    kcal = models.PositiveIntegerField()
    fat = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    saturated_fat = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    carbohydrate = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    sugar = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    added_sugar = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    protein = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    alcohol = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)

    salt = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name="salt (g)",blank=True,default=0.0)
    sodium = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name="sodium (g)",blank=True,default=0.0)
    potassium = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name="potassium (g)",blank=True,default=0.0)
    fiber = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name="fiber (g)",blank=True,default=0.0)
    water = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name="water (ml)",blank=True,default=0.0)

    micro_nutrients = models.ManyToManyField(MicroNutrient,through='ProductMicroNutrient',blank=True)

    def __unicode__(self): return unicode(self.name)

    class Meta:
        ordering = [ 'name','vendor' ]

    def save(self,*args,**kwargs):
        if self.salt == 0 and self.sodium > 0:
            self.salt=self.sodium/0.4
        if self.sodium == 0 and self.salt > 0:
            self.sodium=self.salt*0.4
        super(Product, self).save(*args,**kwargs)

class ProductMicroNutrient(models.Model):
    product = models.ForeignKey(Product)   
    micro_nutrient = models.ForeignKey(MicroNutrient)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='quantity (mg)')

    def __unicode__(self): return unicode(self.micro_nutrient)
    
class MeasureUnit(models.Model):
    name = models.CharField(max_length=1024)
    base = models.CharField(max_length=128,default='g',choices = ( ( "g", "g" ),
                                                                   ( "ml", "ml" ) ))
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __unicode__(self): return unicode(self.name)
    
    class Meta:
        ordering = [ 'name' ]

class FoodDiaryEntry(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(default=datetime.datetime.now)
    product = models.ForeignKey(Product)
    measure_unit = models.ForeignKey(MeasureUnit)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    kcal = models.FloatField(editable=False)
    fat = models.FloatField(editable=False)
    saturated_fat = models.FloatField(editable=False)
    carbohydrate = models.FloatField(editable=False)
    sugar = models.FloatField(editable=False)
    protein = models.FloatField(editable=False)
    alcohol = models.FloatField(editable=False)
    added_sugar = models.FloatField(editable=False)

    salt = models.FloatField(editable=False)
    sodium = models.FloatField(editable=False)
    potassium = models.FloatField(editable=False)
    fiber = models.FloatField(editable=False)
    water = models.FloatField(editable=False)

    future = models.BooleanField(default=False)

    def __unicode__(self): return unicode(self.product)

    class Meta:
        ordering = [ 'time' ]

    def save(self,*args,**kwargs):
        self.kcal=self._kcal()
        self.fat=self._fat()
        self.carbohydrate=self._carbohydrate()
        self.sugar=self._sugar()
        self.protein=self._protein()
        self.added_sugar=self._added_sugar()
        self.alcohol=self._alcohol()
        self.saturated_fat=self._saturated_fat()
        self.salt=self._salt()
        self.sodium=self._sodium()
        self.potassium=self._potassium()
        self.fiber=self._fiber()
        self.water=self._water()
        super(FoodDiaryEntry,self).save(*args,**kwargs)

    def quantity_real(self):
        return self.quantity*self.measure_unit.factor

    def measure_unit_real(self):
        return self.measure_unit.base

    def _kcal(self): return self.product.kcal*self.quantity_real()/100.0
    def _fat(self): return self.product.fat*self.quantity_real()/100.0
    def _alcohol(self): return self.product.alcohol*self.quantity_real()/100.0
    def _carbohydrate(self): return self.product.carbohydrate*self.quantity_real()/100.0
    def _sugar(self): return self.product.sugar*self.quantity_real()/100.0
    def _added_sugar(self): return self.product.added_sugar*self.quantity_real()/100.0
    def _protein(self): return self.product.protein*self.quantity_real()/100.0
    def _saturated_fat(self): return self.product.saturated_fat*self.quantity_real()/100.0
    def _salt(self): return self.product.salt*self.quantity_real()/100.0
    def _sodium(self): return self.product.sodium*self.quantity_real()/100.0
    def _potassium(self): return self.product.potassium*self.quantity_real()/100.0
    def _fiber(self): return self.product.fiber*self.quantity_real()/100.0
    def _water(self): return self.product.water*self.quantity_real()/100.0

# METABOLISMO BASALE
# age     DONNA          UOMO
# 18 - 29 14,7 x P + 496 15,3 x P + 679
# 30- 59   8,7 x P + 829 11,6 x P + 879
# 60-74    9,2 x P + 688 11,9 x P + 700
# >74      9,8 x P + 624 8,4 x P + 819 

class WeightDiaryEntry(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(default=datetime.datetime.now)
    weight = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='weight (kg)')
    base = models.FloatField(editable=False)
    need = models.FloatField(editable=False)

    def save(self,*args,**kwargs):
        self.base=829+8.7*self.weight
        self.need=1.42*self.base
        super(WeightDiaryEntry,self).save(*args,**kwargs)

class Recipe(models.Model):
    name = models.CharField(max_length=1024)
    time = models.DateTimeField(default=datetime.datetime.now)
    final_weight = models.PositiveIntegerField(default=0)
    total_weight = models.PositiveIntegerField(editable=False)

    def __unicode__(self): return unicode(self.name)

    def _total_weight(self):
        total=0
        for rp in self.recipeproduct_set.all():
            total+=rp.quantity_real()
        return total

    def save(self,*args,**kwargs):
        self.total_weight=self._total_weight()
        if self.final_weight==0:
            self.final_weight=self.total_weight
        super(Recipe,self).save(*args,**kwargs)

class RecipeProduct(models.Model):
    recipe = models.ForeignKey(Recipe)
    product = models.ForeignKey(Product)
    measure_unit = models.ForeignKey(MeasureUnit)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __unicode__(self): return unicode(self.product)

    def quantity_real(self):
        return self.quantity*self.measure_unit.factor

class FrequentDiaryEntry(models.Model):
    product = models.ForeignKey(Product)
    measure_unit = models.ForeignKey(MeasureUnit)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __unicode__(self): return unicode(self.product)+" ("+unicode(self.quantity)+" "+unicode(self.measure_unit)+")"


#####


class UsdaNndFoodGroup(models.Model):
    name = models.CharField(max_length=1024)
    usda_id = models.CharField(max_length=1024)

    def __unicode__(self): return unicode(self.name)
    
class UsdaNndFood(models.Model):
    usda_id = models.CharField(max_length=1024)
    food_group = models.ForeignKey(UsdaNndFoodGroup)
    long_description = models.CharField(max_length=1024)
    short_description = models.CharField(max_length=1024)
    common_name = models.CharField(max_length=1024)
    manufacturer_name = models.CharField(max_length=1024)
    survey = models.BooleanField()
    refuse_desc = models.CharField(max_length=1024)
    refuse_perc = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    scientific_name = models.CharField(max_length=1024)
    nitrogen_factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    protein_factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    fat_factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    carbohydrate_factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __unicode__(self): return unicode(self.short_description)

class UsdaNndLangual(models.Model):
    usda_id = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024)

    def __unicode__(self): return unicode(self.description)

class UsdaNndFoodLangualRelation(models.Model):
    food    = models.ForeignKey(UsdaNndFood)
    langual = models.ForeignKey(UsdaNndLangual)
    
    def __unicode__(self): return unicode(self.langual.description)
    
