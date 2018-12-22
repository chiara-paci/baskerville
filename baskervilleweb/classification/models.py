from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
#from django.contrib.contenttypes import generic
from django.db.models import Q 

# Create your models here.

class ArgumentManager(models.Manager):

    # sequenza formata da numeri e range eventualmente seguita da "*"
    # range espressi tra [] come n-m (inclusivi) oppure a,b,c

    def get_by_identifier_selector(self,nfilter):
        exact=True
        if nfilter[-1]=="*":
            exact=False
            nfilter=nfilter[:-1]
        if "[" not in nfilter:
            if exact:
                return self.filter(identifier=nfilter)
            return self.filter(identifier__istartswith=nfilter)
        ranges=[]
        t=nfilter.split("[")
        for token in t:
            if token[-1]!="]":
                ranges.append([token])
                continue
            token=token[:-1]
            if "," not in token:
                s=token.split("-")
                if len(s)==1: 
                    ranges.append([s])
                    continue
                ranges.append(list(range(int(s[0]),int(s[1])+1)))
                continue
            r=[]
            q=token.split(",")
            for a in q:
                if "-" not in a: 
                    r.append(a)
                    continue
                s=a.split("-")
                r+=list(range(int(s[0]),int(s[1])+1))
            ranges.append(r)

        ids=ranges[0]
        oldids=None
        for r in ranges[1:]:
            oldids=ids
            ids=[]
            for i in oldids:
                for s in r:
                    ids.append(str(i)+str(s))
        if exact:
            return self.filter(identifier__in=ids)

        q = Q()
        for identifier in ids:
            q |= Q(identifier__istartswith=identifier)    # | will union all objects 
        return self.filter(q)


class Argument(models.Model):
    parent = models.ForeignKey("self",on_delete=models.PROTECT)
    name = models.CharField(max_length=4096)
    number = models.CharField(max_length=1024)
    identifier = models.CharField(max_length=4096,editable=False,unique=True)
    objects = ArgumentManager()

    class Meta:
        ordering = [ 'identifier' ]

    def __str__(self):
        return str(self.identifier)+" "+str(self.name)

    def parent_identifier(self): return self.parent.identifier

    def save(self, *args, **kwargs):
        if self.parent.id==0:
            self.identifier=self.number
        elif self.parent.parent.id==0:
            self.identifier=str(self.parent.identifier)+"."+str(self.number)
        else:
            self.identifier=str(self.parent.identifier)+str(self.number)
        super(Argument,self).save(*args, **kwargs)

class ArgumentSuffixCollection(models.Model):
    name = models.SlugField(max_length=4096)
    description = models.CharField(max_length=4096)
    phase = models.IntegerField(default=0)
    number = models.CharField(max_length=4096)

    class Meta:
        ordering = [ 'name' ]

    def __str__(self):
        return str(self.name)

    def roots(self):

        L=[]
        if self.phase==0:
            for sel in self.argumentselector_set.all():
                args=Argument.objects.get_by_identifier_selector(sel.pattern)
                L+=list(args)
        else:
            for sel in self.argumentselector_set.all():
                args=ArgumentClassification.objects.get_by_number_selector(sel.pattern)
                L+=list(args)
        return L

class ArgumentSelector(models.Model):
    pattern = models.CharField(max_length=4096,unique=True)
    collection = models.ForeignKey(ArgumentSuffixCollection,on_delete=models.PROTECT)

    def __str__(self):
        return self.pattern


class ArgumentSuffix(models.Model):
    parent = models.ForeignKey("self",on_delete=models.PROTECT)
    collection = models.ForeignKey(ArgumentSuffixCollection,on_delete=models.PROTECT)
    name = models.CharField(max_length=4096)
    number = models.CharField(max_length=1024)
    identifier = models.CharField(max_length=4096,editable=False)

    class Meta:
        ordering = [ 'collection','identifier' ]
        unique_together = [ "collection", "identifier" ]

    def __str__(self):
        return str(self.identifier)+" "+str(self.name)

    def save(self, *args, **kwargs):
        if self.parent.id==0:
            self.identifier=".0"+str(self.collection.number)+str(self.number)
        else:
            self.identifier=str(self.parent.identifier)+str(self.number)
        super(ArgumentSuffix,self).save(*args, **kwargs)

    def parent_identifier(self): return self.parent.identifier


class DecimalNumberManager(models.Manager):

    # sequenza formata da numeri e range eventualmente seguita da "*"
    # range espressi tra [] come n-m (inclusivi) oppure a,b,c

    def get_by_number_selector(self,nfilter):
        exact=True
        if nfilter[-1]=="*":
            exact=False
            nfilter=nfilter[:-1]
        if "[" not in nfilter:
            if exact:
                return self.filter(number=nfilter)
            return self.filter(number__istartswith=nfilter)
        ranges=[]
        t=nfilter.split("[")
        for token in t:
            if token[-1]!="]":
                ranges.append([token])
                continue
            token=token[:-1]
            if "," not in token:
                s=token.split("-")
                if len(s)==1: 
                    ranges.append([s])
                    continue
                ranges.append(list(range(int(s[0]),int(s[1])+1)))
                continue
            r=[]
            q=token.split(",")
            for a in q:
                if "-" not in a: 
                    r.append(a)
                    continue
                s=a.split("-")
                r+=list(range(int(s[0]),int(s[1])+1))
            ranges.append(r)

        ids=ranges[0]
        oldids=None
        for r in ranges[1:]:
            oldids=ids
            ids=[]
            for i in oldids:
                for s in r:
                    ids.append(str(i)+str(s))
        if exact:
            return self.filter(number__in=ids)

        q = Q()
        for number in ids:
            q |= Q(number__istartswith=number)    # | will union all objects 
        return self.filter(q)

class DecimalNumberAbstract(models.Model):
    number = models.CharField(max_length=1024,unique=True)
    name = models.CharField(max_length=4096)
    objects = DecimalNumberManager()

    def __str__(self):
        return self.identifier()+" "+str(self.name)

    def identifier(self):
        return str(self.number)

    def description(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = [ "number" ]

class ArgumentClassification(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]


class LanguageAuxiliaryNumber(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]

class LanguageNumber(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]

class LanguageClassification(models.Model):
    language = models.ForeignKey(LanguageNumber,on_delete=models.PROTECT)
    auxiliaries = models.ManyToManyField(LanguageAuxiliaryNumber,blank=True)
    
    def __str__(self):
        return self.identifier()+" "+self.description()

    def identifier(self):
        I=self.language.identifier()
        for aux in self.auxiliaries.all():
            I+="'"+aux.identifier()
        return I

    def description(self):
        D=str(self.language.name)
        for aux in self.auxiliaries.all():
            D+="/"+str(aux.description())
        return D
            
class PlaceAuxiliaryNumber(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]

class PlaceNumber(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]

class PlaceClassification(models.Model):
    place = models.ForeignKey(PlaceNumber,on_delete=models.PROTECT)
    auxiliaries = models.ManyToManyField(PlaceAuxiliaryNumber,blank=True)

    def __str__(self):
        return self.identifier()+" "+self.description()

    def identifier(self):
        I=self.place.identifier()
        for aux in self.auxiliaries.all():
            I+="'"+aux.identifier()
        return I

    def description(self):
        D=str(self.place.name)
        for aux in self.auxiliaries.all():
            D+="/"+str(aux.name)
        return D
    
class TimeClassification(DecimalNumberAbstract):
    date_start = models.DateField()
    date_end = models.DateField()

    class Meta:
        ordering = [ "number" ]
    
class FormClassification(DecimalNumberAbstract):
    class Meta:
        ordering = [ "number" ]

class ShortClassificationManager(models.Manager):
    def match_classification(self,classification):
        for sc in self.order_by("priority"):
            if sc.id==0:
                continue

            prefix=str(sc.argument.number)
            if str(classification.argument.number)[0:len(prefix)]!=prefix: 
                continue

            sc_ids=sc.forms.all().values("id")
            tg_ids=classification.forms.all().values("id")
            if bool([x for x in sc_ids if x not in tg_ids]): 
                continue

            sc_ids=sc.languages.all().values("id")
            tg_ids=classification.languages.all().values("id")
            if bool([x for x in sc_ids if x not in tg_ids]): 
                continue

            sc_ids=sc.places.all().values("id")
            tg_ids=classification.places.all().values("id")
            if bool([x for x in sc_ids if x not in tg_ids]): 
                continue

            sc_ids=sc.times.all().values("id")
            tg_ids=classification.times.all().values("id")
            if bool([x for x in sc_ids if x not in tg_ids]): 
                continue

            return sc

        return self.get(id=0)

class ShortClassification(models.Model):
    argument = models.ForeignKey(ArgumentClassification,on_delete=models.PROTECT)
    languages = models.ManyToManyField(LanguageClassification,blank=True)
    places = models.ManyToManyField(PlaceClassification,blank=True)
    times = models.ManyToManyField(TimeClassification,blank=True)
    forms = models.ManyToManyField(FormClassification,blank=True)
    label = models.CharField(max_length=1024,unique=True)
    priority = models.PositiveIntegerField()
    objects = ShortClassificationManager()

    class Meta:
        ordering = [ "priority" ]

    def description(self):
        D=self.argument.description()
        for aux in self.languages.all():
            D+=", "+aux.description()
        for aux in self.places.all():
            D+=", "+aux.description()
        for aux in self.times.all():
            D+=", "+aux.description()
        for aux in self.forms.all():
            D+=", "+aux.description()
        return D
        
    def identifier(self):
        return str(self.label)

    def reduced_identifier(self):
        return self.identifier()
        
    def reduced_description(self):
        return str(self.name)

    def __str__(self):
        return self.identifier()+" "+self.description()

    def get_short_identifier(self,classification):
        if self.id==0:
            return classification.identifier()

        sub=str(sc.argument.number)
        prefix=str(self.label)+str(classification.argument.number)[len(sub):]

        sc_ids=sc.forms.all().values("id")
        tg_ids=classification.forms.all().values("id")
        form_ids=[x for x in tg_ids if x not in sc_ids] 
        
        sc_ids=sc.languages.all().values("id")
        tg_ids=classification.languages.all().values("id")
        language_ids=[x for x in tg_ids if x not in sc_ids]
        
        sc_ids=sc.places.all().values("id")
        tg_ids=classification.places.all().values("id")
        place_ids=[x for x in tg_ids if x not in sc_ids]
        
        sc_ids=sc.times.all().values("id")
        tg_ids=classification.times.all().values("id")
        time_ids=[x for x in tg_ids if x not in sc_ids]

        for aux in classification.languages.filter(id__in=language_ids):
            I+="="+aux.identifier()
        for aux in classification.places.filter(id__in=place_ids):
            I+="|"+aux.identifier()
        for aux in classification.times.filter(id__in=time_ids):
            I+="["+aux.identifier()+"]"
        for aux in classification.forms.filter(id__in=form_ids):
            I+="("+aux.identifier()+")"
        return I

class Classification(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

    argument = models.ForeignKey(ArgumentClassification,on_delete=models.PROTECT)
    object_classification = models.CharField(max_length=1024)

    copies_number = models.PositiveIntegerField(default=1)

    languages = models.ManyToManyField(LanguageClassification,blank=True)
    places = models.ManyToManyField(PlaceClassification,blank=True)
    times = models.ManyToManyField(TimeClassification,blank=True)
    forms = models.ManyToManyField(FormClassification,blank=True)

    short = models.ForeignKey(ShortClassification,editable=False,on_delete=models.PROTECT)
    short_identifier = models.CharField(max_length=4096,editable=False)

    class Meta:
        unique_together = [ ("argument", "object_classification"),
                            ("content_type","object_id") ]

    def save(self, *args, **kwargs):
        self.short=ShortClassification.objects.match_classification(self)
        self.short_identifier=self.short.get_short_identifier(self)
        super(Classification, self).save(*args, **kwargs)

    def identifier(self):
        I=self.argument.identifier()+":"+str(self.object_classification)
        if self.object_copy > 0:
            I+=":%02d" % self.object_copy
        for aux in self.languages.all():
            I+="="+aux.identifier()
        for aux in self.places.all():
            I+="|"+aux.identifier()
        for aux in self.times.all():
            I+="["+aux.identifier()+"]"
        for aux in self.forms.all():
            I+="("+aux.identifier()+")"
        return I

    def reduced_identifier(self):
        I=self.argument.identifier()+":"+str(self.object_classification)
        return I
        
    def description(self):
        D=self.argument.description()
        for aux in self.languages.all():
            D+=", "+aux.description()
        for aux in self.places.all():
            D+=", "+aux.description()
        for aux in self.times.all():
            D+=", "+aux.description()
        for aux in self.forms.all():
            D+=", "+aux.description()
        return D
        
    def reduced_description(self):
        return self.argument.description()

    def __str__(self):
        return self.identifier()+" "+self.description()

