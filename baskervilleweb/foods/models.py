from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

User=settings.AUTH_USER_MODEL

# Create your models here.

class AbstractName(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self): return str(self.name)

    class Meta:
        ordering = [ 'name' ]
        abstract = True

class Vendor(AbstractName): pass
class MicroNutrientClass(AbstractName): pass

class MicroNutrient(AbstractName):
    nutrient_class = models.ForeignKey(MicroNutrientClass,on_delete=models.PROTECT)
    rda = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                            verbose_name='rda (mg)',default=0.0)
    rda_max = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                verbose_name='rda max (mg)',default=0.0)

class ProductCategory(AbstractName): pass
    
class Product(models.Model):
    name = models.CharField(max_length=1024)
    category = models.ForeignKey(ProductCategory,on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT)
    value_for = models.CharField(max_length=128,default='100 g',
                                 choices = ( ( "100 g", "100 g" ),
                                             ( "100 ml", "100 ml" ) ))
    high_processed = models.BooleanField(default=False)
    kcal           = models.PositiveIntegerField()
    fat            = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    saturated_fat  = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    carbohydrate   = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    sugar          = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    added_sugar    = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    protein        = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    alcohol        = models.FloatField(validators=[validators.MinValueValidator(0.0)],blank=True,default=0.0)
    salt           = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                       verbose_name="salt (g)",blank=True,default=0.0)
    sodium         = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                       verbose_name="sodium (g)",blank=True,default=0.0)
    potassium      = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                       verbose_name="potassium (g)",blank=True,default=0.0)
    fiber          = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                       verbose_name="fiber (g)",blank=True,default=0.0)
    water          = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                       verbose_name="water (ml)",blank=True,default=0.0)

    micro_nutrients = models.ManyToManyField(MicroNutrient,through='ProductMicroNutrient',blank=True)

    class Meta:
        ordering = [ 'name','vendor' ]

    def save(self,*args,**kwargs):
        if self.salt == 0 and self.sodium > 0:
            self.salt=self.sodium/0.4
        if self.sodium == 0 and self.salt > 0:
            self.sodium=self.salt*0.4
        super(Product, self).save(*args,**kwargs)

    def __str__(self): return str(self.name)

class ProductMicroNutrient(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)   
    micro_nutrient = models.ForeignKey(MicroNutrient,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='quantity (mg)')

    def __str__(self): return str(self.micro_nutrient)
    
class MeasureUnit(AbstractName):
    base = models.CharField(max_length=128,default='g',choices = ( ( "g", "g" ),
                                                                   ( "ml", "ml" ) ))
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])

class FoodDiaryEntry(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    measure_unit = models.ForeignKey(MeasureUnit,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    kcal          = models.FloatField(editable=False)
    fat           = models.FloatField(editable=False)
    saturated_fat = models.FloatField(editable=False)
    carbohydrate  = models.FloatField(editable=False)
    sugar         = models.FloatField(editable=False)
    protein       = models.FloatField(editable=False)
    alcohol       = models.FloatField(editable=False)
    added_sugar   = models.FloatField(editable=False)
    salt          = models.FloatField(editable=False)
    sodium        = models.FloatField(editable=False)
    potassium     = models.FloatField(editable=False)
    fiber         = models.FloatField(editable=False)
    water         = models.FloatField(editable=False)

    future = models.BooleanField(default=False)

    def __str__(self): return str(self.product)

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

class WeightDiaryEntry(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)
    weight = models.FloatField(validators=[validators.MinValueValidator(0.0)],verbose_name='weight (kg)')
    base = models.FloatField(editable=False)
    need = models.FloatField(editable=False)

    ## QUI
    def save(self,*args,**kwargs):
        # https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation
        # Men 	BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
        # Women BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161 

        age=self.user.date_of_birth-self.time
        year=age.days/365.0

        base=(10*self.weight) + (6.25*self.user.height) - (5*year)
        if self.user.gender=="male":
            base+=5
        else:
            base-=161
            
        self.base=base

        if self.user.lifestyle=="sedentary":
            self.need=1.53*self.base
        elif self.user.lifestyle=="active":
            self.need=1.76*self.base
        else:
            self.need=2.25*self.base
        super(WeightDiaryEntry,self).save(*args,**kwargs)

class Recipe(AbstractName):
    time = models.DateTimeField(default=timezone.now)
    final_weight = models.PositiveIntegerField(default=0)
    total_weight = models.PositiveIntegerField(editable=False)

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
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    measure_unit = models.ForeignKey(MeasureUnit,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __str__(self): return str(self.product)

    def quantity_real(self):
        return self.quantity*self.measure_unit.factor

class FrequentDiaryEntry(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    measure_unit = models.ForeignKey(MeasureUnit,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)])

    def __str__(self): return str(self.product)+" ("+str(self.quantity)+" "+str(self.measure_unit)+")"


#####


class UsdaNndFoodGroup(AbstractName):
    usda_id = models.CharField(max_length=1024)
    
class UsdaNndFood(models.Model):
    usda_id = models.CharField(max_length=1024)
    food_group = models.ForeignKey(UsdaNndFoodGroup,on_delete=models.PROTECT)
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

    def __str__(self): return str(self.short_description)

class UsdaNndLangual(models.Model):
    usda_id = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024)

    def __str__(self): return str(self.description)

class UsdaNndFoodLangualRelation(models.Model):
    food    = models.ForeignKey(UsdaNndFood,on_delete=models.PROTECT)
    langual = models.ForeignKey(UsdaNndLangual,on_delete=models.PROTECT)
    
    def __str__(self): return str(self.langual.description)
    
