from django.db import models
from django.core import validators
from django.utils.functional import cached_property

import re

# Create your models here.

class NameAbstractManager(models.Manager):
    def deserialize(self,ser):
        obj,created=self.get_or_create(name=ser)
        return obj
        

class NameAbstract(models.Model):
    name = models.CharField(max_length=4096,unique=True)

    objects=NameAbstractManager()

    class Meta:
        abstract = True
        ordering = [ 'name' ]

    def __str__(self): 
        return self.name

    def __serialize__(self): return self.name

class Tool(NameAbstract): pass
class FoodCategory(NameAbstract): pass
class RecipeCategory(NameAbstract): pass

class StepSequenceManager(NameAbstractManager):
    def deserialize(self,ser):
        obj,created=self.get_or_create(name=ser["name"])
        for step in ser["steps"]:
            Step.objects.deserialize(obj,step)
        return obj

class StepSequence(NameAbstract):
    #parent = models.ForeignKey('self',on_delete=models.SET_NULL,blank=True,null=True)

    #class Meta:
    #    ordering = [ 'name' ]

    objects=StepSequenceManager()

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

    def __serialize__(self):
        return {
            "name": self.name,
            "steps": [ s.__serialize__() for s in self.step_set.all() ]
        }

class StepManager(models.Manager):
    def deserialize(self,sequence,ser):
        obj,created=self.update_or_create(
            sequence=sequence,
            pos=ser["pos"],
            defaults={
                "description": ser["description"]
            }
        )
        for tool_name,use_new in ser["tools"]:
            tool=Tool.objects.deserialize(tool_name)
            StepToolRelation.objects.update_or_create(
                step=obj,
                tool=tool,
                defaults={
                    "use_new": use_new
                }
            )
        return obj

class Step(models.Model):
    description = models.CharField(max_length=8192)
    sequence = models.ForeignKey(StepSequence,on_delete=models.PROTECT)
    pos = models.PositiveIntegerField()
    #tools = models.ManyToManyField(Tool,blank=True,through='StepToolRelation')

    objects=StepManager()

    class Meta:
        ordering = [ "sequence","pos" ]
        unique_together = [ "sequence","pos" ]

    def __str__(self): return self.description

    def __serialize__(self):
        return {
            "description": self.description,
            "pos": self.pos,
            "tools":[ (rel.tool.__serialize__(),
                       rel.use_new) for rel in self.steptoolrelation_set.all() ]
        }

class StepToolRelation(models.Model):
    tool = models.ForeignKey(Tool,on_delete=models.PROTECT)
    step = models.ForeignKey(Step,on_delete=models.PROTECT)
    use_new = models.BooleanField(default=False)

    def __str__(self):
        return "%s/%s" % (self.tool,self.step)

###

class RecipeManager(NameAbstractManager):
    def deserialize(self,ser):
        defaults={
            "serving": ser["serving"],
            "execution": StepSequence.objects.get(name=ser["execution"]),
            "category": RecipeCategory.objects.get(name=ser["category"]),
        }

        obj,created=self.update_or_create(name=ser["name"],defaults=defaults)

        for g_ser,factor in ser["ingredient_groups"]:
            grp=IngredientGroup.objects.get(name=g_ser)
            RecipeIngredientGroupRelation.objects.update_or_create(
                group=grp,
                recipe=obj,
                defaults={"factor": factor}
            )

        for a_ser,factor in ser["ingredient_alternatives"]:
            alt=IngredientAlternative.objects.get(name=a_ser)
            RecipeIngredientAlternativeRelation.objects.update_or_create(
                alternative=alt,
                recipe=obj,
                defaults={"factor": factor}
            )

        return obj

class Cell(object):
    def __init__(self,val,td="td",colspan=1,rowspan=1,style=""):
        self.td=td
        self.val=val
        self.colspan=colspan
        self.rowspan=rowspan
        self.style=style

class Table(object):

    def __init__(self,num_cols):
        self._num_cols=num_cols
        self.data=[]

    def add_title(self,name,level=0):
        row=[]
        if level==0:
            row.append( Cell(name,td="th",style="title",colspan=self._num_cols) )
            self.data.append(row)
            return
        row.append( Cell("",style="empty") )
        row.append( Cell(name,td="th",style="sub",colspan=self._num_cols-1) )
        self.data.append(row)

    def _data_cell(self,d,**kwargs):
        if type(d) is str:
            return Cell(d,**kwargs)
        kwargs=kwargs.copy()
        if "style" in kwargs:
            kwargs["style"]+=" "+d[1]
        else:
            kwargs["style"]=d[1]
        return Cell(d[0],**kwargs)

    def add_row(self,data,level=0):
        row=[]
        num_data=len(data)
        if level>0:
            row.append( Cell("",style="empty",colspan=level) )
        row.append( self._data_cell(data[0],style="datafirst",
                                    colspan=self._num_cols-level-len(data)) )
        for d in data[1:]:
            row.append( self._data_cell(d,style="data") )
        self.data.append(row)
            

class Recipe(NameAbstract):
    category = models.ForeignKey(RecipeCategory,on_delete=models.PROTECT)
    serving = models.PositiveIntegerField(blank=True,default=4,
                                          validators=[validators.MinValueValidator(1)])
    execution = models.ForeignKey(StepSequence,on_delete=models.PROTECT)

    objects=RecipeManager()

    def __serialize__(self):
        return {
            "name": self.name,
            "category": self.category.name,
            "execution": self.execution.name,
            "serving": self.serving,
            "ingredient_groups": [ 
                (rel.group.name,
                 rel.factor) for rel in self.recipeingredientgrouprelation_set.all() ],
            "ingredient_alternatives": [ 
                (rel.alternative.name,
                 rel.factor) for rel in self.recipeingredientalternativerelation_set.all() ],
            
        }
        
    def _ingredient_row_data(self,factor,ingredient):
        name=ingredient.food.name
        if ingredient.preparation is not None:
            preparation=ingredient.preparation.name
        else:
            preparation=""
        if ingredient.measure.base=="qb":
            return ("q.b.","right"),name,preparation,"",""

        quantity="%2.3f" % (factor*ingredient.quantity)
        quantity=quantity.strip("0").rstrip(".")
        quantity_base=str(int(round(factor*ingredient.quantity_base)))

        return ( 
            (quantity,"right"),ingredient.measure.abbreviation,
            name,preparation,
            (quantity_base,"right light"),(ingredient.measure.base,"light"),
        )

    class IngredientWrapper(object):
        def __init__(self,factor,ingredient):
            self._factor=factor
            self._ingredient=ingredient

        def __getattribute__(self,name):
            if name not in [ "_factor","_ingredient","quantity", "quantity_base", "quantity_str", "quantity_base_str" ]:
                return self._ingredient.__getattribute__(name)
            if name in [ "_factor","_ingredient" ]:
                return object.__getattribute__(self,name)
            if name=="quantity":
                return self._factor*self._ingredient.quantity
            if name=="quantity_base":
                return self._factor*self._ingredient.quantity_base
            if name=="quantity_base_str":
                return str(int(round(self._factor*self._ingredient.quantity_base)))
            quantity="%2.3f" % (self._factor*self._ingredient.quantity)
            quantity=quantity.strip("0").rstrip(".")
            return quantity
            

    def ingredient_groups(self):
        groups={}
        for g_rel in self.recipeingredientgrouprelation_set.all():
            groups[g_rel.group.name]=[]
            for i_rel in g_rel.group.ingredientingredientgrouprelation_set.all():
                factor=g_rel.factor*i_rel.factor
                groups[g_rel.group.name].append(self.IngredientWrapper(factor,i_rel.ingredient))
        return groups.items()
                            
    def ingredient_alternatives(self):
        alternatives={}
        for a_rel in self.recipeingredientalternativerelation_set.all():
            groups={}
            for g_rel in a_rel.alternative.ingredientalternativegrouprelation_set.all():
                groups[g_rel.group.name]=[]
                for i_rel in g_rel.group.ingredientingredientgrouprelation_set.all():
                    factor=a_rel.factor*g_rel.factor*i_rel.factor
                    groups[g_rel.group.name].append(self.IngredientWrapper(factor,i_rel.ingredient))
            alternatives[a_rel.alternative.name]=groups.items()
        return alternatives.items()
        

    def ingredients_table(self):
        tab=Table(8)

        for g_rel in self.recipeingredientgrouprelation_set.all():
            tab.add_title(g_rel.group.name)
            for i_rel in g_rel.group.ingredientingredientgrouprelation_set.all():
                factor=g_rel.factor*i_rel.factor
                data=self._ingredient_row_data(factor,i_rel.ingredient)
                tab.add_row(data,level=1)

        for a_rel in self.recipeingredientalternativerelation_set.all():
            tab.add_title(a_rel.alternative.name)
            n=1
            for g_rel in a_rel.alternative.ingredientalternativegrouprelation_set.all():
                tab.add_title("alternative %d: %s" % (n,g_rel.group.name),level=1)
                for i_rel in g_rel.group.ingredientingredientgrouprelation_set.all():
                    factor=a_rel.factor*g_rel.factor*i_rel.factor
                    data=self._ingredient_row_data(factor,i_rel.ingredient)
                    tab.add_row(data,level=1)
                n+=1

        return tab



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


class MeasureUnitManager(NameAbstractManager):
    def deserialize(self,ser):
        defaults={
            "base": ser["base"],
            "abbreviation": ser["abbreviation"],
            "factor": ser["factor"],
            "plural": ser["plural"],
        }
        obj,created=self.update_or_create(
            name=ser["name"],
            apply_to=ser["apply_to"],
            defaults=defaults
        )
        return obj


class MeasureUnit(NameAbstract):
    name = models.CharField(max_length=4096)
    base = models.CharField(max_length=128,default='g',choices = ( ( "g",  "g" ),
                                                                   ( "ml", "ml" ),
                                                                   ( "qb", "qb") ))
    abbreviation = models.CharField(max_length=1024)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    plural = models.CharField(max_length=4096,blank=True,null=True)
    apply_to = models.CharField(max_length=4096,blank=True,null=True)

    objects=MeasureUnitManager()

    def __serialize__(self):
        return {
            "name": self.name,
            "base": self.base,
            "abbreviation": self.abbreviation,
            "factor": self.factor,
            "plural": self.plural,
            "apply_to": self.apply_to,
        }

    
    class Meta:
        ordering = [ 'name' ]
        unique_together = [ ("name","apply_to") ]

    def __str__(self):
        if not self.apply_to: return self.name
        return "%s (%s)" % (self.name,self.apply_to)

    @cached_property
    def name_plural(self):
        if self.plural: return self.plural
        return self.name

    def ingredient_count(self):
        return self.ingredient_set.all().count()

class FoodManager(NameAbstractManager):
    def deserialize(self,ser):
        defaults={
            "plural": ser["plural"],
            "gender": ser["gender"],
            "category": FoodCategory.objects.deserialize(ser["name"])
        }

        obj,created=self.update_or_create(
            name=ser["name"],
            defaults=defaults
        )
        return obj


class Food(NameAbstract):
    category = models.ForeignKey(FoodCategory,on_delete=models.PROTECT)
    plural = models.CharField(max_length=4096,blank=True,null=True)
    gender = models.CharField(max_length=128,default='masculine',choices = ( 
        ( "masculine", "masculine" ),
        ( "neuter", "neuter" ),
        ( "feminine", "feminine" ) ))

    objects=FoodManager()

    def __serialize__(self):
        return {
            "name": self.name,
            "category": self.category.__serialize__(),
            "plural": self.plural,
            "gender": self.gender,
        }


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
class Vendor(NameAbstract): pass

def get_bulk_product_vendor():
    vendor,create=Vendor.objects.get_or_create(name="bulk product")
    return vendor.id

class ProductManager(NameAbstractManager):
    def deserialize(self,ser):
        defaults={
            "vendor": Vendor.objects.deserialize(ser["name"]),
            "food": Food.objects.get(name=ser["food"]),
        }

        obj,created=self.update_or_create(
            name=ser["name"],
            defaults=defaults
        )

        for r in ser["retailers"]:
            retailer=Retailer.objects.deserialize(r)
            obj.retailers.add(retailer)

        return obj

class Product(NameAbstract):
    food = models.ForeignKey(Food,on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT,default=get_bulk_product_vendor)
    retailers = models.ManyToManyField(Retailer,blank=True)

    objects=ProductManager()

    def __serialize__(self):
        return {
            "name": self.name,
            "food": self.food.name,
            "vendor": self.vendor.__serialize__(),
            "retailers": [ o.__serialize__() for o in self.retailers.all() ]
        }

### QUI

class IngredientManager(models.Manager):
    def deserialize(self,ser):
        kwargs={
            "quantity": ser["quantity"],
            "inlist": ser["inlist"],
            "food": Food.objects.get(name=ser["food"]),
            "measure": MeasureUnit.objects.get(name=ser["measure"][0],
                                               apply_to=ser["measure"][1]),
        }

        if ser["preparation"] is not None:
            kwargs["preparation"]=StepSequence.objects.get(name=ser["preparation"])
        else:
            kwargs["preparation"]=None

        obj,created=self.get_or_create(**kwargs)
        return obj

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

    objects=IngredientManager()

    def __serialize__(self):
        ret={
            "food": self.food.name,
            "measure": ( self.measure.name,self.measure.apply_to ),
            "quantity": self.quantity,
            "inlist": self.inlist,
        }
        if self.preparation is not None:
            ret["preparation"]= self.preparation.name
        else:
            ret["preparation"]=None
        return ret


    class Meta:
        ordering = [ "food", "quantity", "measure", 'preparation' ]

    def __str__(self): 
        qta=("%2.2f" % self.quantity).strip("0").rstrip(".")

        S="%s %s %s" % (str(self.food),qta,self.measure.abbreviation)
        if self.preparation:
            S+=" "+self.preparation.name
        return S

    @cached_property
    def quantity_base(self):
        return self.quantity*self.measure.factor

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

class IngredientGroupManager(NameAbstractManager):
    def deserialize(self,ser):
        defaults={}

        if ser["preparation"] is not None:
            defaults["preparation"]=StepSequence.objects.get(name=ser["preparation"])
        else:
            defaults["preparation"]=None

        obj,created=self.update_or_create(name=ser["name"],defaults=defaults)

        for i_ser,factor in ser["ingredients"]:
            ingr=Ingredient.objects.deserialize(i_ser)
            IngredientIngredientGroupRelation.objects.update_or_create(
                group=obj,
                ingredient=ingr,
                defaults={"factor": factor}
            )

        return obj

class IngredientGroup(NameAbstract): 
    #ingredients = models.ManyToManyField(Ingredient,blank=True)
    preparation = models.ForeignKey(StepSequence,blank=True,null=True,
                                    on_delete=models.PROTECT)
    objects=IngredientGroupManager()

    def __serialize__(self):
        ret={
            "name": self.name,
            "ingredients": [ 
                (rel.ingredient.__serialize__(),
                 rel.factor) for rel in self.ingredientingredientgrouprelation_set.all() 
            ]
        }

        if self.preparation is not None:
            ret["preparation"]= self.preparation.name
        else:
            ret["preparation"]=None
        return ret



class IngredientIngredientGroupRelation(models.Model):
    ingredient = models.ForeignKey(Ingredient,on_delete=models.PROTECT)
    group = models.ForeignKey(IngredientGroup,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)

    @cached_property
    def quantity(self):
        return self.factor*self.ingredient.quantity

    @cached_property
    def quantity_base(self):
        return self.factor*self.ingredient.quantity_base

class IngredientAlternativeManager(NameAbstractManager):
    def deserialize(self,ser):
        obj,created=self.get_or_create(name=ser["name"])

        for g_name,factor in ser["groups"]:
            grp=IngredientGroup.objects.get(name=g_name)
            IngredientAlternativeGroupRelation.objects.update_or_create(
                group=grp,
                alternative=obj,
                defaults={"factor": factor}
            )

        return obj


class IngredientAlternative(NameAbstract): 
    objects=IngredientAlternativeManager()

    def __serialize__(self):
        return {
            "name": self.name,
            "groups": [ 
                (rel.group.name,
                 rel.factor) for rel in self.ingredientalternativegrouprelation_set.all() ]
        }

class IngredientAlternativeGroupRelation(models.Model):
    alternative = models.ForeignKey(IngredientAlternative,on_delete=models.PROTECT)
    group = models.ForeignKey(IngredientGroup,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)
    
class RecipeIngredientGroupRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    group = models.ForeignKey(IngredientGroup,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)

class RecipeIngredientAlternativeRelation(models.Model):
    recipe = models.ForeignKey(Recipe,on_delete=models.PROTECT)
    alternative = models.ForeignKey(IngredientAlternative,on_delete=models.PROTECT)
    factor = models.FloatField(validators=[validators.MinValueValidator(0.0)],default=1.0)


class RecipeSetManager(NameAbstractManager):
    def deserialize(self,ser):
        obj,created=self.get_or_create(name=ser["name"])

        for r_ser,l_ser,serving in ser["recipes"]:
            recipe=Recipe.objects.get(name=r_ser)
            label=RecipeLabel.objects.deserialize(l_ser)
            
            RecipeRecipeSetRelation.objects.update_or_create(
                set=obj,
                recipe=recipe,
                defaults={
                    "serving": serving,
                    "label": label,
                }
            )
        return obj

class RecipeSet(NameAbstract):
    objects=RecipeSetManager()
    def __serialize__(self):
        return {
            "name": self.name,
            "recipes": [ 
                (rel.recipe.name,
                 rel.label.name,
                 rel.serving) for rel in self.reciperecipesetrelation_set.all() ]
        }

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
        
