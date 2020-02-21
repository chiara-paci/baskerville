from django.db import models
from django.core import validators
from django.utils.functional import cached_property

import re

# Create your models here.

class NameAbstract(models.Model):
    name = models.CharField(max_length=4096)

    class Meta:
        abstract = True

    def __str__(self): 
        return self.name

class Tool(NameAbstract): pass
class FoodCategory(NameAbstract): pass
class RecipeCategory(NameAbstract): pass

class StepSequence(NameAbstract):
    #parent = models.ForeignKey('self',on_delete=models.SET_NULL,blank=True,null=True)

    class Meta:
        order_with_respect_to = 'name'

    def tools(self):
        tools={}
        for step in self.step_set.all():
            for tool in step.tools.all():
                if not tool.name in tools: tools[tool.name]=0
                tools[tool.name]+=1
        # for seq in self.stepsequence_set.all():
        #     for tool_name,num in seq.tools():
        #         if not tool_name in tools: tools[tool_name]=0
        #         tools[tool_name]+=num
        return tools.items()

    def steps(self):
        steps=[]
        for step in self.step_set.all():
            steps.append(step)
        # for seq in self.stepsequence_set.all():
        #     for step in seq.steps():
        #         steps.append(step)
        return steps

class Step(models.Model):
    description = models.CharField(max_length=8192)
    sequence = models.ForeignKey(StepSequence,on_delete=models.PROTECT)
    tools = models.ManyToManyField(Tool,blank=True)

    class Meta:
        order_with_respect_to = 'sequence'

    def __str__(self): return self.description

class Recipe(NameAbstract):
    category = models.ForeignKey(RecipeCategory,on_delete=models.PROTECT)
    serving = models.PositiveIntegerField(blank=True,default=4,
                                          validators=[validators.MinValueValidator(1)])
    execution = models.ForeignKey(StepSequence,on_delete=models.PROTECT)

    execution_tools = models.ManyToManyField(Tool,blank=True,through="ExecutionToolRelation",related_name="recipe_execution_set")
    ingredient_tools = models.ManyToManyField(Tool,blank=True,through="IngredientToolRelation",related_name="recipe_ingredient_set")

    def ingredients(self):
        t=[str(x) for x in self.ingredient_set.all().filter(inlist=True)]
        return ", ".join(t)

    # def tools(self):
    #     tools={}
    #     for tool_name,num in self.execution.tools():
    #         if not tool_name in tools: tools[tool_name]=0
    #         tools[tool_name]+=num

    #     for ing in self.ingredient_set.all():
    #         if not ing.preparation: continue
    #         for tool_name,num in ing.preparation.tools():
    #             if not tool_name in tools: tools[tool_name]=0
    #             tools[tool_name]+=num
    #     return tools.items()

    def tools(self):
        tools={}
        #for tool 

        for step in self.execution.step_set.all():
            rel_list=[]
            for tool in step.tools.all():
                rel,created=ExecutionToolRelation.objects.get_or_create(recipe=self,tool=tool,step=step)
                rel_list.append(rel.pk)
            ExecutionToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()
        for ing in self.ingredient_set.all():
            for step in ing.preparation.step_set.all():
                rel_list=[]
                for tool in step.tools.all():
                    rel,created=IngredientToolRelation.objects.get_or_create(recipe=self,ingredient=ing,tool=tool,step=step)
                    rel_list.append(rel.pk)
                IngredientToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()


    def save(self,*args,**kwargs):
        NameAbstract.save(self,*args,**kwargs)
        for step in self.execution.step_set.all():
            rel_list=[]
            for tool in step.tools.all():
                rel,created=ExecutionToolRelation.objects.get_or_create(recipe=self,tool=tool,step=step)
                rel_list.append(rel.pk)
            ExecutionToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()
        for ing in self.ingredient_set.all():
            for step in ing.preparation.step_set.all():
                rel_list=[]
                for tool in step.tools.all():
                    rel,created=IngredientToolRelation.objects.get_or_create(recipe=self,ingredient=ing,tool=tool,step=step)
                    rel_list.append(rel.pk)
                IngredientToolRelation.objects.filter(recipe=self).exclude(pk__in=rel_list).delete()


class ExecutionToolRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    tool = models.ForeignKey(Tool,on_delete=models.PROTECT)
    step = models.ForeignKey(Step,on_delete=models.PROTECT)
    use_new = models.BooleanField(default=False)

    def __str__(self):
        return "%s: %s/%s" % (self.recipe,self.tool,self.step)

class MeasureUnit(NameAbstract):
    base = models.CharField(max_length=128,default='g',choices = ( ( "g",  "g" ),
                                                                   ( "ml", "ml" ),
                                                                   ( "qb", "qb") ))
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    plural = models.CharField(max_length=4096,blank=True,null=True)
    
    class Meta:
        ordering = [ 'name' ]

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

class Ingredient(models.Model):
    food = models.ForeignKey(Food,on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    quantity = models.FloatField(validators=[validators.MinValueValidator(0.0)],
                                 blank=True,null=True)
    measure = models.ForeignKey(MeasureUnit,
                                blank=True,null=True,on_delete=models.PROTECT)
    preparation = models.ForeignKey(StepSequence,blank=True,null=True,on_delete=models.PROTECT)
    inlist=models.BooleanField(default=True,blank=True)

    def __str__(self): 
        return str(self.food)

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

       
class IngredientToolRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    tool = models.ForeignKey(Tool,on_delete=models.PROTECT)
    step = models.ForeignKey(Step,on_delete=models.PROTECT)
    ingredient = models.ForeignKey(Ingredient,on_delete=models.PROTECT)
    use_new = models.BooleanField(default=False)

    def __str__(self):
        return "%s/%s: %s/%s" % (self.recipe,self.ingredient,self.tool,self.step)
        
