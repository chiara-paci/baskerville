from django.db import models
from django.core import validators
from django.utils.functional import cached_property

import re

# Create your models here.

class NameAbstract(models.Model):
    name = models.CharField(max_length=4096)

    class Meta:
        abstract = True
        ordering = [ 'name' ]

    def __str__(self): 
        return self.name

class Tool(NameAbstract): pass
class FoodCategory(NameAbstract): pass
class RecipeCategory(NameAbstract): pass

class StepSequence(NameAbstract):
    #parent = models.ForeignKey('self',on_delete=models.SET_NULL,blank=True,null=True)

    #class Meta:
    #    ordering = [ 'name' ]

    def tools(self):
        tools={}
        for step in self.step_set.all():
            for rel in step.steptoolrelation_set.all():
                if not rel.tool.name in tools: tools[rel.tool.name]=0
                if tools[rel.tool.name]==0: 
                    tools[rel.tool.name]=1
                    continue
                if rel.use_new:
                    tools[rel.tool.name]+=1
        return tools.items()

    def steps(self):
        steps=[]
        for step in self.step_set.all():
            steps.append(step)
        return steps

class Step(models.Model):
    description = models.CharField(max_length=8192)
    sequence = models.ForeignKey(StepSequence,on_delete=models.PROTECT)
    pos = models.PositiveIntegerField()
    #tools = models.ManyToManyField(Tool,blank=True,through='StepToolRelation')

    class Meta:
        ordering = [ "sequence","pos" ]
        unique_together = [ "sequence","pos" ]

    def __str__(self): return self.description

class StepToolRelation(models.Model):
    tool = models.ForeignKey(Tool,on_delete=models.PROTECT)
    step = models.ForeignKey(Step,on_delete=models.PROTECT)
    use_new = models.BooleanField(default=False)

    def __str__(self):
        return "%s/%s" % (self.tool,self.step)

###


class Recipe(NameAbstract):
    category = models.ForeignKey(RecipeCategory,on_delete=models.PROTECT)
    serving = models.PositiveIntegerField(blank=True,default=4,
                                          validators=[validators.MinValueValidator(1)])
    execution = models.ForeignKey(StepSequence,on_delete=models.PROTECT)

    #execution_tools = models.ManyToManyField(Tool,blank=True,through="StepToolRelation",related_name="recipe_execution_set")
    #ingredient_tools = models.ManyToManyField(Tool,blank=True,through="IngredientToolRelation",related_name="recipe_ingredient_set")

    # def ingredients(self):
    #     t=[str(x) for x in self.ingredient_set.all().filter(inlist=True)]
    #     return ", ".join(t)

    # def tools(self):
    #     tools={}
    #     #for tool 

    #     for step in self.execution.step_set.all():
    #         rel_list=[]
    #         for tool in step.tools.all():
    #             rel,created=StepToolRelation.objects.get_or_create(recipe=self,tool=tool,step=step)
    #             rel_list.append(rel.pk)
    #         StepToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()
    #     for ing in self.ingredient_set.all():
    #         for step in ing.preparation.step_set.all():
    #             rel_list=[]
    #             for tool in step.tools.all():
    #                 rel,created=IngredientToolRelation.objects.get_or_create(recipe=self,ingredient=ing,tool=tool,step=step)
    #                 rel_list.append(rel.pk)
    #             IngredientToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()


    # def save(self,*args,**kwargs):
    #     NameAbstract.save(self,*args,**kwargs)
    #     for step in self.execution.step_set.all():
    #         rel_list=[]
    #         for tool in step.tools.all():
    #             rel,created=StepToolRelation.objects.get_or_create(recipe=self,tool=tool,step=step)
    #             rel_list.append(rel.pk)
    #         StepToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()
    #     for ing in self.ingredient_set.all():
    #         for step in ing.preparation.step_set.all():
    #             rel_list=[]
    #             for tool in step.tools.all():
    #                 rel,created=IngredientToolRelation.objects.get_or_create(recipe=self,ingredient=ing,tool=tool,step=step)
    #                 rel_list.append(rel.pk)
    #             IngredientToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()



class MeasureUnit(NameAbstract):
    base = models.CharField(max_length=128,default='g',choices = ( ( "g",  "g" ),
                                                                   ( "ml", "ml" ),
                                                                   ( "qb", "qb") ))
    abbreviation = models.CharField(max_length=1024)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    plural = models.CharField(max_length=4096,blank=True,null=True)
    apply_to = models.CharField(max_length=4096,blank=True,null=True)
    
    class Meta:
        ordering = [ 'name' ]

    def __str__(self):
        if not self.apply_to: return self.name
        return "%s (%s)" % (self.name,self.apply_to)

    @cached_property
    def name_plural(self):
        if self.plural: return self.plural
        return self.name


class Food(NameAbstract):
    category = models.ForeignKey(FoodCategory,on_delete=models.PROTECT)
    plural = models.CharField(max_length=4096,blank=True,null=True)
    gender = models.CharField(max_length=128,default='masculine',choices = ( 
        ( "masculine", "masculine" ),
        ( "neuter", "neuter" ),
        ( "feminine", "feminine" ) ))

    def __str__(self):
        if self.plural: return self.plural
        return self.name

    @cached_property
    def il_plural(self):
        if not self.plural: return self.il_singular
        if self.gender=="feminine":
            return "le %s" % self.plural
        if self.plural[0] in [ "a","e","i","o","u","y","z","x" ]:
            return "gli %s" % self.plural
        if self.plural[0:2] in [ "ps","pn","gn" ]:
            return "gli %s" % self.plural
        if self.plural[0]=="s":
            if self.plural[1] in [ "a","e","i","o","u","y" ]:
                return "i %s" % self.plural
            return "gli %s" % self.plural
        return "i %s" % self.plural

    @cached_property
    def il_singular(self):
        if self.name[0] in [ "a","e","i","o","u" ]:
            return "l'%s" % self.name
        if self.gender=="feminine":
            return "la %s" % self.name
        if self.name[0] in [ "y","z","x" ]:
            return "lo %s" % self.name
        if self.name[0:2] in [ "ps","pn","gn" ]:
            return "lo %s" % self.name
        if self.name[0]=="s":
            if self.name[1] in [ "a","e","i","o","u","y" ]:
                return "il %s" % self.name
            return "lo %s" % self.name
        return "il %s" % self.name
                
    @cached_property
    def lo_plural(self):
        if not self.plural: return self.lo_singular
        if self.gender=="feminine":
            return "le"
        return "li"

    @cached_property
    def lo_singular(self):
        if self.gender=="feminine":
            return "la"
        return "lo"

class Retailer(NameAbstract): pass

class Vendor(NameAbstract):
    name = models.CharField(max_length=4096,unique=True)

def get_bulk_product_vendor():
    vendor,create=Vendor.objects.get_or_create(name="bulk product")
    return vendor.id

class Product(NameAbstract):
    food = models.ForeignKey(Food,on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT,default=get_bulk_product_vendor)
    retailers = models.ManyToManyField(Retailer,blank=True)

class Ingredient(models.Model):
    food = models.ForeignKey(Food,on_delete=models.PROTECT)
    # recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                 blank=True,null=True)
    measure = models.ForeignKey(MeasureUnit,
                                blank=True,null=True,on_delete=models.PROTECT)
    preparation = models.ForeignKey(StepSequence,blank=True,null=True,
                                    on_delete=models.PROTECT)
    inlist=models.BooleanField(default=True,blank=True)

    def __str__(self): 
        S="%s %f %s" % (str(self.food),self.quantity,self.measure.abbreviation)
        if self.preparation:
            S+=" "+self.preparation.name
        return S

    @cached_property
    def il(self):
        singular=(self.quantity==1 and self.measure==self.food.name)
        if singular:
            return self.food.il_singular
        return self.food.il_plural

    @cached_property
    def lo(self):
        singular=(self.quantity==1 and self.measure==self.food.name)
        if singular:
            return self.food.lo_singular
        return self.food.lo_plural

    @cached_property
    def format_preparation(self):
        if not self.preparation: return []
        params={
            "il": self.il,
            "lo": self.lo
        }
        ret=[]
        for step in self.preparation.step_set.all():
            ret.append(str(step) % params)
            #ret.append(str(step)) # % params)
        return ret

    @cached_property
    def format_quantity(self):
        # {% if ing.quantity %}{{ ing.quantity|floatformat:"-2" }} {% if ing.measure %}{{ ing.measure }}{% endif %}{% endif %}</td>
        if self.measure.base=="qb": return "q.b."
        if self.quantity<=0: return "q.b."
        qta=re.sub( r'\.?0+$','', ("%.2f" % self.quantity) )
        if self.quantity==1:
            return "%s %s" % (qta,self.measure.name)
        else:
            return "%s %s" % (qta,self.measure.name_plural)
            
    @cached_property
    def format_conversion(self):
        if self.measure.base=="qb": return ""
        if (self.measure.name==self.measure.base) and (self.measure.factor==1): return ""
        q_conv=re.sub( r'\.?0+$','', ("%.2f" % (self.quantity*self.measure.factor) ) )
        return "(%s %s)" % (q_conv,self.measure.base)

class IngredientGroup(NameAbstract): 
    ingredients = models.ManyToManyField(Ingredient,blank=True)

class IngredientAlternative(NameAbstract): pass
    
class RecipeIngredientGroupRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    group = models.ForeignKey(IngredientGroup,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)

class RecipeIngredientAlternativeRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    alternative = models.ForeignKey(IngredientAlternative,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)

class IngredientAlternativeGroupRelation(models.Model):
    alternative = models.ForeignKey(IngredientAlternative,on_delete=models.PROTECT)
    group = models.ForeignKey(IngredientGroup,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)

class RecipeSet(NameAbstract): pass
class RecipeLabel(NameAbstract): pass

class RecipeRecipeSetRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    set = models.ForeignKey(RecipeSet,on_delete=models.PROTECT)
    label = models.ForeignKey(RecipeLabel,on_delete=models.PROTECT)
    serving = models.PositiveIntegerField(blank=True,default=2,
                                          validators=[validators.MinValueValidator(1)])


# class IngredientToolRelation(models.Model):
#     #recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
#     tool = models.ForeignKey(Tool,on_delete=models.PROTECT)
#     step = models.ForeignKey(Step,on_delete=models.PROTECT)
#     ingredient = models.ForeignKey(Ingredient,on_delete=models.PROTECT)
#     use_new = models.BooleanField(default=False)

#     def __str__(self):
#         return "%s: %s/%s" % (self.ingredient,self.tool,self.step)
        
