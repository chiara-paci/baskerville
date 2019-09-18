# -*- coding: utf-8 -*-

from django.db import models
import django.template.defaultfilters
from django.db.models import Max
from django.utils.functional import cached_property
# Create your models here.

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
#from django.contrib.contenttypes import generic
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete,pre_save,pre_delete
from django.db.models.signals import m2m_changed

import django.dispatch

position_changed = django.dispatch.Signal(providing_args=["instance"])
valid_changed = django.dispatch.Signal(providing_args=["instance"])

#from santaclara_base.models import PositionAbstract

import re

def custom_model_list(model_list):

    sections=["Language",
              "Place",
              "Time span",
              "Person",
              "Category",
              "Author",
              "Publisher",
              "Book",
              "Publication",
              "Migr",
              "Repository",]

    ret={}
    for sec in sections:
        ret[sec]=[]

    for model_dict in model_list:
        if model_dict["model_label"] in ["repositorycachebook","repositorycacheauthor","repositoryfailedisbn",]:
            ret["Repository"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "timepoint","timespan","datemodifier" ]:
            ret["Time span"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "language","languagefamily","languagefamilyrelation",
                                          "languagefamilyfamilyrelation","languagevarietytype","languagevariety" ]:
            ret["Language"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "placetype","place","alternateplacename","placerelation" ]:
            ret["Place"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "article","articleauthorrelation","issuetype",
                                          "issue","publication","volumetype","volume" ]:
            ret["Publication"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "nameformat","nametype","nameformatcollection","personcache",
                                          "person","personnamerelation" ]:
            ret["Person"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "categorytreenode","category","categoryrelation",
                                          "categorytimespanrelation", "categoryplacerelation", 
                                          "categorypersonrelation", 
                                          "categorylanguagerelation" ]:
            ret["Category"].append(model_dict)
            continue
        
        if model_dict["model_label"] in [ "author","authorrole","authorrelation" ]:
            ret["Author"].append(model_dict)
            continue

        if model_dict["model_label"] in [ "migrauthor","migrpublisherriviste" ]:
            ret["Migr"].append(model_dict)
            continue
        
        if model_dict["model_label"] in [ "publisherstate","publisheraddress","publisherisbn","publisher",
                                          "publisheraddresspublisherrelation" ]:
            ret["Publisher"].append(model_dict)
            continue
        
        ret["Book"].append(model_dict)

    xret=[]
    for sec in sections:
        xret.append( (sec,ret[sec]))
    
    return xret

class PositionAbstract(models.Model): 
    """ Classe astratta per gestire oggetti posizionabili all'interno di un elenco.
    
    Definisce il campo *pos* (posizione) come intero positivo. 

    Emette il segnale :any:`santaclara_base.signals.position_changed`
    quando la posizione viene modificata.

    Un modello che estende la classe PositionAbstract e ridefinisce
    __init__() o save() deve ricordarsi di richiamare rispettivamente
    :any:`PositionAbstract.my_action_post_init
    <santaclara_base.models.PositionAbstract.my_action_post_init>` e
    :any:`PositionAbstract.my_action_post_save
    <santaclara_base.models.PositionAbstract.my_action_post_save>`.

    Un modello che estende la classe PositionAbstract con eredità
    multipla e in modo che save() e __init__() siano ereditati da
    un'altra classe (quindi con PositionAbstract non primo modello tra
    i padri), deve ridefinirli in modo o da richiamare
    PositionAbstract.save() e PositionAbstract.__init__() oppure da
    utilizzare esplicitamente
    :any:`PositionAbstract.my_action_post_init
    <santaclara_base.models.PositionAbstract.my_action_post_init>` e
    :any:`PositionAbstract.my_action_post_save
    <santaclara_base.models.PositionAbstract.my_action_post_save>`.
    """

    #: Posizione.
    pos = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def __init__(self,*args,**kwargs):
        super(PositionAbstract, self).__init__(*args, **kwargs)
        self.my_action_post_init(*args,**kwargs)

    def save(self,*args,**kwargs):
        super(PositionAbstract,self).save(*args,**kwargs)
        self.my_action_post_save(*args,**kwargs)

    def my_action_post_save(self,*args,**kwargs):
        """ Se un modello che estende PositionAbstract sovrascrive
        save() e non richiama esplicitamente PositionAbstract.save(),
        oppure se in caso di eredità multipla il save() del modello
        non è PositionAbstract.save(), nel nuovo save() dev'essere
        richiamata questa funzione, passandole gli stessi parametri di
        save(). """
        if self.__original_pos!=self.pos:
            position_changed.send(self.__class__,instance=self)
            self.__original_pos = self.pos
        
    def my_action_post_init(self,*args,**kwargs):
        """ Se un modello che estende PositionAbstract sovrascrive
        __init__() e non richiama esplicitamente PositionAbstract.__init__(),
        oppure se in caso di eredità multipla il __init__() del modello
        non è PositionAbstract.__init__(), nel nuovo __init__() dev'essere
        richiamata questa funzione, passandole gli stessi parametri di
        __init__(). """
        self.__original_pos = self.pos


class LabeledAbstract(models.Model):
    label = models.SlugField(unique=True)
    description = models.CharField(max_length=1024)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.label)

    def clean(self,*args,**kwargs):
        self.label = self.label.lower()
        super(LabeledAbstract, self).clean(*args, **kwargs)

### time span

class DateModifier(PositionAbstract):
    name = models.CharField(max_length=1024)
    reverse = models.BooleanField(default=False)

    class Meta:
        ordering = [ 'pos' ]

    def __str__(self):
        if self.id==0: return ""
        if not self.name: return "-"
        return str(self.name)

    def save(self,*args,**kwargs):
        super(DateModifier, self).save(*args, **kwargs)
        for obj in self.timepoint_set.all():
            obj.save()

class TimePoint(models.Model):
    date = models.IntegerField()
    modifier = models.ForeignKey(DateModifier,blank=True,default=0,on_delete=models.PROTECT)

    class Meta:
        ordering = [ 'modifier','date' ]
        unique_together= [ 'modifier','date' ]

    def __str__(self):
        U=str(abs(self.date))
        if self.modifier.id!=0:
            U+=" "+str(self.modifier)
        return U

    def save(self,*args,**kwargs):
        if not self.modifier:
            self.modifier=DateModifier.objects.get(id=0)
        if self.modifier.reverse:
            self.date=-abs(self.date)
        else:
            self.date=abs(self.date)
        super(TimePoint, self).save(*args, **kwargs)

    def begins(self):
        return "; ".join([str(x) for x in self.begin_set.all()])
        
    def ends(self):
        return "; ".join([str(x) for x in self.end_set.all()])
        
    def time_spans(self):
        L=[str(x) for x in self.begin_set.all()]
        L+=[str(x) for x in self.end_set.all()]
        L=list(set(L))
        return "; ".join(L)

class TimeSpan(models.Model):
    begin = models.ForeignKey(TimePoint,related_name="begin_set",on_delete=models.PROTECT)
    end   = models.ForeignKey(TimePoint,related_name="end_set",on_delete=models.PROTECT)
    name  = models.CharField(max_length=4096,blank=True)

    def __str__(self):
        if self.name:
            return str(self.name)
        return str(self.begin)+"-"+str(self.end)

    class Meta:
        ordering = [ 'begin','end' ]

    def categories(self):
        return "; ".join([str(x.category) for x in self.categorytimespanrelation_set.all()])


### language

class Language(models.Model):
    name = models.CharField(max_length=4096)

    def __str__(self): return self.name

    def families(self):
        return "; ".join([str(x.family) for x in self.languagefamilyrelation_set.all()])

    def varieties(self):
        return "; ".join([str(x) for x in self.languagevariety_set.all()])

class LanguageFamily(models.Model):
    name = models.CharField(max_length=4096)

    def __str__(self): return self.name

    def parents(self):
        return "; ".join([str(x.parent) for x in self.parent_set.all()])

    def children(self):
        return "; ".join([str(x.child) for x in self.child_set.all()])

    def languages(self):
        return "; ".join([str(x.language) for x in self.languagefamilyrelation_set.all()])

class LanguageFamilyRelation(models.Model):
    language = models.ForeignKey(Language,on_delete=models.PROTECT)
    family = models.ForeignKey(LanguageFamily,on_delete=models.PROTECT)

    def __str__(self): 
        return str(self.family)+"/"+str(self.language)

class LanguageFamilyFamilyRelation(models.Model):
    parent = models.ForeignKey(LanguageFamily,related_name="child_set",on_delete=models.PROTECT)
    child = models.ForeignKey(LanguageFamily,related_name="parent_set",on_delete=models.PROTECT)

    def __str__(self): 
        return str(self.parent)+"/"+str(self.child)

    class Meta:
        ordering = ["parent","child"]
    
    
class LanguageVarietyType(models.Model):
    name = models.CharField(max_length=4096)    

    def __str__(self): return self.name

class LanguageVariety(models.Model):
    name = models.CharField(max_length=4096,blank=True)
    language = models.ForeignKey(Language,on_delete=models.PROTECT)
    type = models.ForeignKey(LanguageVarietyType,default=1,on_delete=models.PROTECT)

    def __str__(self):
        if self.type.id==1:
            return str(self.language)
        if not self.name:
            return str(self.language)
        return str(self.language)+" ("+str(self.name)+")"

### place

class PlaceType(models.Model):
    name = models.CharField(max_length=4096)

    def __str__(self): return self.name

class Place(models.Model):
    name = models.CharField(max_length=4096,unique=True)
    type = models.ForeignKey(PlaceType,on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def alternate_names(self):
        return "; ".join([str(x.name) for x in self.alternateplacename_set.all()])

    def areas(self):
        return "; ".join([str(x.area) for x in self.area_set.all()])

    def places(self):
        return "; ".join([str(x.place) for x in self.place_set.all()])

    class Meta:
        ordering = [ "name" ]

class AlternatePlaceName(models.Model):
    place = models.ForeignKey(Place,on_delete=models.PROTECT)
    name = models.CharField(max_length=4096)
    note = models.CharField(max_length=65536,blank=True)

    def __str__(self):
        return self.name

class PlaceRelation(models.Model):
    place = models.ForeignKey(Place,related_name="area_set",on_delete=models.PROTECT)
    area = models.ForeignKey(Place,related_name="place_set",on_delete=models.PROTECT)

    def __str__(self): 
        return str(self.area)+"/"+str(self.place)

    class Meta:
        ordering = ["area","place"]

### person

class NameFormat(LabeledAbstract):
    pattern = models.CharField(max_length=1024)

    class Meta:
        ordering = ["label"]

    def save(self, *args, **kwargs):
        super(NameFormat, self).save(*args, **kwargs)
        for coll in self.long_format_set.all():
            coll.save()
        for coll in self.short_format_set.all():
            coll.save()
        for coll in self.ordering_format_set.all():
            coll.save()
        for coll in self.list_format_set.all():
            coll.save()

class NameType(LabeledAbstract): pass

RE_NAME_SEP=re.compile("('| |-)")

VONS=["von","di","da","del","della","dell","dello","dei","degli","delle","de","d","la","lo",
      "dal","dalla","dall","dallo","dai","dagli","dalle","al","ibn"]

ROMANS=["I","II","III","IV","V","VI","VII","VIII","IX","X",
        "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX",
        "XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII","XXIX","XXX",
        "XXXI","XXXII","XXXIII","XXXIV","XXXV","XXXVI","XXXVII","XXXVIII","XXXIX","XL",
        "XLI","XLII","XLIII","XLIV","XLV","XLVI","XLVII","XLVIII","XLIX","L"]


class NameFormatCollectionManager(models.Manager):
    def get_preferred(self,num_fields):
        preferred_list=self.all().filter(preferred=True)
        for format_c in preferred_list:
            fields=format_c.fields
            if len(fields)==num_fields: 
                return format_c
        format_max_num=-1
        format_max=None
        for format_c in self.all():
            fields=format_c.fields
            if len(fields)==num_fields: 
                return format_c
            if len(fields)>format_max_num:
                format_max_num=len(fields)
                format_max=format_c
        return format_max

    def get_format_for_name(self,search):
        if not search:
            return self.get_preferred(0),[]
        if search.lower().replace(".","") in [ "av","aavv" ]:
            return self.get_preferred(0),[]

        t=RE_NAME_SEP.split(search)        
        names=[]
        t_vons=""
        for n in range(0,len(t)):
            if not t[n]: continue
            if t[n] in [ " ","'" ]:
                if t_vons:
                    t_vons+=t[n]
                continue
            if t[n]=="-":
                if t_vons:
                    t_vons+="-"
                else:
                    names[-1]+="-"
                continue
            if t[n].lower() not in VONS:
                if names and names[-1].endswith("-"):
                    names[-1]+=t[n].capitalize()
                else:
                    names.append(t_vons+t[n].capitalize())
                t_vons=""
                continue
            t_vons+=t[n]
        return self.get_preferred(len(names)),names

class NameFormatCollection(LabeledAbstract):
    long_format = models.ForeignKey(NameFormat,related_name='long_format_set',on_delete=models.PROTECT)
    short_format = models.ForeignKey(NameFormat,related_name='short_format_set',on_delete=models.PROTECT)
    list_format = models.ForeignKey(NameFormat,related_name='list_format_set',on_delete=models.PROTECT)
    ordering_format = models.ForeignKey(NameFormat,related_name='ordering_format_set',on_delete=models.PROTECT)

    preferred = models.BooleanField(default=False)

    objects = NameFormatCollectionManager()

    def save(self, *args, **kwargs):
        super(NameFormatCollection, self).save(*args, **kwargs)
        for person in self.person_set.all():
            person.update_cache()

    @cached_property
    def fields(self):
        L=["name","surname"]
        long_name=str(self.long_format.pattern)
        short_name=str(self.short_format.pattern)
        list_name=str(self.list_format.pattern)
        ordering_name=str(self.ordering_format.pattern)

        for s in "VALURNIC":
            long_name=long_name.replace("{{"+s+"|","{{")
            short_name=short_name.replace("{{"+s+"|","{{")
            list_name=list_name.replace("{{"+s+"|","{{")
            ordering_name=ordering_name.replace("{{"+s+"|","{{")
        
        names=[]
        for f in [long_name,short_name,list_name,ordering_name]:
            L=[x.replace("{{","").replace("}}","") for x in re.findall(r'{{.*?}}',f)]
            for name in L:
                if name in names: continue
                names.append(name)
        return names

    ### Sintassi dei formati
    #   {{<name_type>}}: <name_type> 
    #   {{C|<name_type>}}: <name_type> (capitalized)
    #   {{V|<name_type>}}: <name_type> (capitalized except von, de, ecc.)
    #   {{L|<name_type>}}: <name_type> (lowered)
    #   {{U|<name_type>}}: <name_type> (uppered)
    #   {{A|<name_type>}}: <name_type> as integer in arabic 
    #   {{R|<name_type>}}: <name_type> as integer in roman upper
    #   {{N|<name_type>}}: <name_type> (lowered and with space => _)
    #   {{I|<name_type>}}: iniziali (Gian Uberto => G. U.)

    def apply_formats(self,names):
        long_name=str(self.long_format.pattern)
        short_name=str(self.short_format.pattern)
        list_name=str(self.list_format.pattern)
        ordering_name=str(self.ordering_format.pattern)
        list_upper=str(self.list_format.pattern)
        list_lower=str(self.list_format.pattern)

        for key,rel in list(names.items()):
            val_f=rel.formatted()
            
            long_name=long_name.replace("{{"+key+"}}",val_f["norm"])
            short_name=short_name.replace("{{"+key+"}}",val_f["norm"])
            list_name=list_name.replace("{{"+key+"}}",val_f["norm"])
            ordering_name=ordering_name.replace("{{"+key+"}}",val_f["norm"])
            list_upper=list_upper.replace("{{"+key+"}}",val_f["norm_upper"])
            list_lower=list_lower.replace("{{"+key+"}}",val_f["norm_lower"])

            for k in "VALURNIC":
                long_name=long_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                short_name=short_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                list_name=list_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                ordering_name=ordering_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                if k in "AR":
                    list_upper=list_upper.replace("{{"+k+"|"+key+"}}",val_f[k])
                    list_lower=list_lower.replace("{{"+k+"|"+key+"}}",val_f[k])
                else:
                    list_upper=list_upper.replace("{{"+k+"|"+key+"}}",val_f["norm_upper"])
                    list_lower=list_lower.replace("{{"+k+"|"+key+"}}",val_f["norm_lower"])

        return long_name,short_name,list_name,ordering_name,list_upper[0],list_lower[0]

class PersonCache(models.Model):
    long_name = models.CharField(max_length=4096,default="-")
    short_name = models.CharField(max_length=4096,default="-")
    list_name = models.CharField(max_length=4096,default="-")
    ordering_name = models.CharField(max_length=4096,default="-")
    upper_initial = models.CharField(max_length=4,default="-")
    lower_initial = models.CharField(max_length=4,default="-")

    class Meta:
        ordering = ["ordering_name"]
        db_table = 'bibliography_personcache'

    def __str__(self): return self.list_name

class PersonManager(models.Manager):

    def search_names(self,names):
        qset=self.all()
        if len(names)==0: return qset
        #D=[]
        for name in names:
            if name.endswith("."):
                name=name[:-1]
                qset=qset.filter(personnamerelation__value__istartswith=name)
            elif len(name)==1:
                qset=qset.filter(personnamerelation__value__istartswith=name)
            else:
                qset=qset.filter(personnamerelation__value__iexact=name)

        # if qset.count()>0: return qset.select_related("cache")
        # if len(names)==1: return qset.select_related("cache")
        # if len(names)==2:
        #     newnames=[ " ".join(names) ]
        #     return self.search_names(newnames)
        # L=len(names)
        # for n in range(0,L-1):
        #     newnames=names[0:n] + [ " ".join(names[n:n+2])] + names[n+2:L]
        #     qset=self.search_names(newnames)
        #     if qset.count()>0: return qset.select_related("cache")
        return qset.select_related("cache")
    
    def filter_by_name(self,search):
        search=search.replace(" , "," ")
        search=search.replace(", "," ")
        search=search.replace(" ,"," ")
        search=search.replace(","," ")

        if search.lower() in [ "--","","- -","-","aavv","aa.vv.","aa. vv."]:
            format_c=NameFormatCollection.objects.get(label="aavv")
            qset=self.all().filter(format_collection=format_c)
            return qset

        t_name=search.lower().split(" ")
        return self.search_names(t_name)

    def look_for(self,name_list):
        old={}
        new=[]
        for name in name_list:
            qset=self.filter_by_name(name)
            if qset.count():
                old[name]=(qset.first())
            else:
                new.append(name)
        return old,new

    def create_by_names(self,format_collection,**kwargs):
        obj=self.create(format_collection=format_collection)
        for key,val in list(kwargs.items()):
            name_type,created=NameType.objects.get_or_create(label=key)
            rel,created=PersonNameRelation.objects.get_or_create(person=obj,name_type=name_type,
                                                                 defaults={"value": val})
            if not created:
                rel.value=val
                rel.save()
        return obj


class Person(models.Model):
    format_collection = models.ForeignKey(NameFormatCollection,on_delete=models.PROTECT)
    cache = models.OneToOneField(PersonCache,editable=False,null=True,on_delete=models.PROTECT)
    names = models.ManyToManyField(NameType,through='PersonNameRelation',blank=True)

    objects = PersonManager()

    class Meta:
        ordering = ["cache"]
        db_table = 'bibliography_person'

    def __str__(self):
        return self.list_name()

    def long_name(self): return str(self.cache.long_name)
    def short_name(self): return str(self.cache.short_name)
    def ordering_name(self): return str(self.cache.ordering_name)
    def list_name(self): return str(self.cache.list_name)
    def upper_initial(self): return str(self.cache.upper_initial)
    def lower_initial(self): return str(self.cache.lower_initial)

    def save(self, *args, **kwargs):
        if not self.cache:
            self.cache = PersonCache.objects.create()
        super(Person, self).save(*args, **kwargs)
        self.update_cache()

    def update_cache(self):
        names={}
        for rel in self.personnamerelation_set.all():
            names[str(rel.name_type.label)]=rel
        long_name,short_name,list_name,ordering_name,upper_initial,lower_initial=self.format_collection.apply_formats(names)
        self.cache.long_name     = long_name
        self.cache.short_name    = short_name
        self.cache.list_name     = list_name
        self.cache.ordering_name = ordering_name
        self.cache.upper_initial = upper_initial
        self.cache.lower_initial = lower_initial
        self.cache.save()

class PersonNameRelation(models.Model):
    person = models.ForeignKey(Person,on_delete=models.PROTECT)
    name_type = models.ForeignKey(NameType,on_delete=models.PROTECT)
    value = models.CharField(max_length=4096,default="-",db_index=True)
    case_rule = models.CharField(max_length=128,choices=[ ("latin","latin"),
                                                          ("turkic","turkic") ],
                                 default="latin")

    def __str__(self): return str(self.value)

    def save(self, *args, **kwargs):
        super(PersonNameRelation, self).save(*args, **kwargs)
        self.person.update_cache()

    def _upper(self,x):
        if self.case_rule=="latin":
            return x.upper()
        x=x.replace("ı","I")
        x=x.replace("i","İ")
        return x.upper()

    def _lower(self,x):
        if self.case_rule=="latin":
            return x.lower()
        x=x.replace("I","ı")
        x=x.replace("İ","i")
        return x.lower()

    def _capitalize(self,x):
        if self.case_rule=="latin":
            return x.capitalize()
        return self._upper(x[0])+self._lower(x[1:])

    ### Sintassi dei formati
    #   {{<name_type>}}: <name_type> 
    #   {{C|<name_type>}}: <name_type> (capitalized)
    #   {{V|<name_type>}}: <name_type> (capitalized except von, de, ecc.)
    #   {{L|<name_type>}}: <name_type> (lowered)
    #   {{U|<name_type>}}: <name_type> (uppered)
    #   {{A|<name_type>}}: <name_type> as integer in arabic 
    #   {{R|<name_type>}}: <name_type> as integer in roman upper
    #   {{N|<name_type>}}: <name_type> (lowered and with space => _)
    #   {{I|<name_type>}}: iniziali (Gian Uberto => G. U.)

    def formatted(self):
        val=str(self.value)
        val_f={}
        t=RE_NAME_SEP.split(val)
        #t=map(lambda x: self._capitalize(x),RE_NAME_SEP.split(val))
        vons_t=[]
        norm_t=[]
        for x in t:
            if self._lower(x) in VONS:
                vons_t.append(self._lower(x))
            else:
                if len(x)==1 and x.isalpha():
                    vons_t.append(self._upper(x)+".")
                else:
                    vons_t.append(self._capitalize(x))
            if len(x)==1 and x.isalpha():
                norm_t.append(x+".")
            else:
                norm_t.append(x)

        cap_t=[self._capitalize(x) for x in norm_t]
        val_norm="".join(norm_t)
        val_f["L"]=self._lower(val)
        val_f["U"]=self._upper(val)
        val_f["N"]=self._lower(val).replace(" ","_")
        val_f["I"]=". ".join([x[0].upper() for x in list(filter(bool,val.split(" ")))])+"."
        val_f["C"]="".join(cap_t)
        val_f["V"]="".join(vons_t)

        if val.isdigit():
            val_f["R"]=ROMANS[int(val)-1]
            val_f["A"]="%3.3d" % int(val)
        else:
            val_f["R"]=""
            val_f["A"]=""

        val_f["norm"]=val_norm
        val_f["norm_upper"]=self._upper(val_norm)
        val_f["norm_lower"]=self._lower(val_norm)
        return val_f

    #     long_name=long_name.replace("{{"+key+"}}",val_norm)
    #     short_name=short_name.replace("{{"+key+"}}",val_norm)
    #     list_name=list_name.replace("{{"+key+"}}",val_norm)
    #     ordering_name=ordering_name.replace("{{"+key+"}}",val_norm)

    #     for k in "VALURNIC":
    #         long_name=long_name.replace("{{"+k+"|"+key+"}}",val_f[k])
    #         short_name=short_name.replace("{{"+k+"|"+key+"}}",val_f[k])
    #         list_name=list_name.replace("{{"+k+"|"+key+"}}",val_f[k])
    #         ordering_name=ordering_name.replace("{{"+k+"|"+key+"}}",val_f[k])

    # return long_name,short_name,list_name,ordering_name






        
### category

class CategoryTreeNodeManager(models.Manager):

    def roots(self):
        return self.filter(level=0)

    def until_level(self,level,only_category=True):
        if not only_category:
            return self.filter(level__lte=level)
        return self.filter(level__lte=level,is_category=True)

    def branch_nodes(self,base_node,level,only_category=True):
        if not only_category:
            return self.filter(level=level,node_id__istartswith=base_node.node_id+":")
        return self.filter(level=level,node_id__istartswith=base_node.node_id+":",is_category=True)

    def update_category(self,cat): 
        ctype = ContentType.objects.get_for_model(Category)
        for cat_node in self.filter(content_type=ctype,object_id=cat.id):
            level=int(cat_node.level)
            old_node_id=str(cat_node.node_id)
            parent_node_id=":".join(old_node_id.split(":")[:-1])
            if parent_node_id:
                new_node_id=parent_node_id+":"+cat.label
            else:
                new_node_id=cat.label                
            cat_node.node_id=new_node_id
            cat_node.save()
            if not cat_node.has_children: return
            cat_children=list(self.filter(node_id__istartswith=old_node_id+":",level=level+1))
            for child in cat_children:
                self.reparent(new_node_id,level,child)

    def remove_category(self,cat): 
        ctype = ContentType.objects.get_for_model(Category)
        node_ids=[]
        for cat_node in self.filter(content_type=ctype,object_id=cat.id):
            node_ids.append(cat_node.node_id)
            self.filter(node_id__istartswith=cat_node.node_id+':').delete()
            cat_node.delete()

    def create_category(self,cat): 
        newobj=self.create(content_object=cat,node_id=cat.label,has_children=False,level=0)
        newobj.save()
        return newobj

    def reparent(self,parent_node_id,parent_level,cat_node):
        ret=[]
        old_node_id=str(cat_node.node_id)
        old_level=int(cat_node.level)
        rel_node_id=old_node_id.split(":")[-1]
        if parent_node_id:
            new_node_id=parent_node_id+":"+rel_node_id
        else:
            new_node_id=rel_node_id
        if parent_level>=0:
            new_level=parent_level+1
        else:
            new_level=0

        cat_node.node_id=new_node_id
        cat_node.level=new_level
        cat_node.save()

        ret.append(("R",cat_node))

        if not cat_node.has_children: return ret

        cat_children=list(self.filter(node_id__istartswith=old_node_id+":"))
        for cch_node in cat_children:
            new_cch_node_id=str(cch_node.node_id).replace(old_node_id+":",new_node_id+":",1)
            new_cch_level=int(cch_node.level)-old_level+new_level
            cch_node.node_id=new_cch_node_id
            cch_node.level=new_cch_level
            cch_node.save()
            ret.append(("R",cch_node))

        return ret

    def clone(self,parent_node_id,parent_level,cat_node):
        ret=[]
        old_node_id=str(cat_node.node_id)
        old_level=int(cat_node.level)
        rel_node_id=old_node_id.split(":")[-1]
        if parent_node_id:
            new_node_id=parent_node_id+":"+rel_node_id
        else:
            new_node_id=rel_node_id
        if parent_level>=0:
            new_level=parent_level+1
        else:
            new_level=0

        newobj=self.create(content_object=cat_node.content_object,
                           node_id=new_node_id,
                           has_children=cat_node.has_children,
                           level=new_level)
        newobj.save()
        ret.append(("C",newobj))
        if not cat_node.has_children: return ret

        cat_children=list(self.filter(node_id__istartswith=old_node_id+":"))
        for cch_node in cat_children:
            new_cch_node_id=str(cch_node.node_id).replace(old_node_id+":",new_node_id+":",1)
            new_cch_level=int(cch_node.level)-old_level+new_level
            newobj=self.create(content_object=cch_node.content_object,
                               node_id=new_cch_node_id,
                               has_children=cch_node.has_children,
                               level=new_cch_level)
            newobj.save()
            ret.append(("C",newobj))

        return ret

    def add_child_category(self,parent,child):
        parent_nodes=list(parent.tree_nodes.all())
        child_nodes=list(child.tree_nodes.all())

        cn=child_nodes[0]
        startind=0
        new_objects=[]
        if len(child_nodes)==1 and child_nodes[0].level==0:
            ## l'unico child è un rootnode
            fn=parent_nodes[0]
            new_objects=self.reparent(str(fn.node_id),int(fn.level),cn)
            startind=1
            fn.has_children=True
            fn.save()

        for fn in parent_nodes[startind:]:
            new_objects+=self.clone(str(fn.node_id),int(fn.level),cn)
            fn.has_children=True
            fn.save()

        return new_objects

    def remove_child_category(self,parent,child): 
        parent_nodes=list(parent.tree_nodes.all())
        child_nodes=list(child.tree_nodes.all())

        del_list=[]
        
        for fn in parent_nodes:
            fn_node_id=str(fn.node_id)
            for cn in child_nodes:
                cn_node_id=str(cn.node_id)
                cn_rel_node_id=cn_node_id.split(":")[-1]
                if cn_node_id==fn_node_id+":"+cn_rel_node_id:
                    del_list.append((fn,cn))
                    break
        
        if len(del_list)==len(child_nodes):
            objs=self.clone("",-1,child_nodes[0])
            for action,obj in objs:
                obj.save()

        for parent,node in del_list:
            self.remove_branch(node)
            parent.has_children=bool(self.filter(node_id__istartswith=str(parent.node_id)+":").exists())
            parent.save()

    def update_child_category(self,old_parent,old_child,new_parent,new_child):
        if not old_parent and not old_child: return
        if (old_parent==new_parent) and (old_child==new_child): return
        self.remove_child_category(old_parent,old_child)
        self.add_child_category(new_parent,new_child)

    def remove_branch(self,basenode):
        base_node_id=str(basenode.node_id)
        self.filter(node_id__istartswith=base_node_id+":").delete()
        self.filter(node_id=base_node_id).delete()

    def add_category_relation(self,cat,child):
        parent_nodes=list(cat.tree_nodes.all())

        ret=[]
        for fn in parent_nodes:
            new_node_id=str(fn.node_id)+":"+str(child.id)
            new_level=int(fn.level)+1
            newobj=self.create(content_object=child,
                               node_id=new_node_id,
                               has_children=False,
                               level=new_level)
            ret.append(("C",newobj))
            fn.has_children=True
            fn.save()
        return ret

    def remove_category_relation(self,cat,child):
        parent_nodes=list(cat.tree_nodes.all())

        node_ids=[]
        for fn in parent_nodes:
            node_ids.append(str(fn.node_id)+":"+str(child.id))
        self.filter(node_id__in=node_ids).delete()

        for fn in parent_nodes:
            fn.has_children=bool(self.filter(node_id__istartswith=str(fn.node_id)+":").exists())
            fn.save()

    def update_category_relation(self,old_cat,old_child,new_cat,new_child):
        if not old_cat and not old_child: return
        if (old_cat==new_cat) and (old_child==new_child): return
        self.remove_category_relation(old_cat,old_child)
        self.add_category_relation(new_cat,new_child)

    def get_num_objects(self,catnode):
        if not catnode.is_category: return 1
        N=self.filter(node_id__istartswith=catnode.node_id+":",is_category=False).values("content_type","object_id").distinct().count()
        return N

    def max_level(self,only_cat=True):
        if not only_cat:
            return self.all().aggregate(Max('level'))["level__max"]
        return self.filter(is_category=True).aggregate(Max('level'))["level__max"]

class CategoryTreeNode(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

    node_id = models.CharField(max_length=4096,unique=True)
    has_children = models.BooleanField()
    level = models.PositiveIntegerField()
    objects = CategoryTreeNodeManager()

    label = models.CharField(max_length=4096,editable=False)
    label_children = models.CharField(max_length=4096,editable=False)
    is_category = models.BooleanField(editable=False)

    num_objects = models.PositiveIntegerField(editable=False)

    def branch_depth(self,only_cat=True):
        if only_cat:
            ret=CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",is_category=True).aggregate(Max('level'))["level__max"]
        else:
            ret=CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":").aggregate(Max('level'))["level__max"]
        if not ret: return 0
        return ret

    def branch_level_size(self,level,only_cat=True):
        if only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",
                                                   level=level,is_category=True).count()
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",level=level).count()
        
    def branch(self,only_cat=True):
        if only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",is_category=True)
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":")

    def __str__(self):
        U= "%3d %s" % (int(self.level),str(self.node_id))
        return U

    def direct_size(self):
        if not self.is_category: return 0
        return self.content_object.child_set.count()

    class Meta:
        ordering = [ "node_id" ]

    def save(self, *args, **kwargs):
        self.label_children="_"+str(self.node_id).replace(":","_")
        t=str(self.node_id).split(":")
        if len(t)==1: 
            self.label=""
        else:
            self.label="_"+"_".join(t[:-1])
        self.is_category=( self.content_type.model_class() == Category )
        self.num_objects = CategoryTreeNode.objects.get_num_objects(self)
        super(CategoryTreeNode, self).save(*args, **kwargs)

class CategoryManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        class CategoryQueryset(models.query.QuerySet):
            def all_in_branch(self,parent_id):
                parent=Category.objects.get(id=int(parent_id))
                children_ids=[parent.id]
                for catnode in parent.tree_nodes.all():
                    L=catnode.branch()
                    children_ids+=[x.object_id for x in list(L)]
                children_ids=list(set(children_ids))
                return self.filter(id__in=children_ids)
        return CategoryQueryset(Category)

    def query_set_branch(self,queryset,parent_id):
        parent=Category.objects.get(id=int(parent_id))
        children_ids=[parent.id]
        for catnode in parent.tree_nodes.all():
            L=catnode.branch()
            children_ids+=[x.object_id for x in list(L)]
        children_ids=list(set(children_ids))
        return queryset.filter(id__in=children_ids)
        

    def all_in_branch(self,parent_id):
        return self.get_query_set().all_in_branch(parent_id)

    def merge(self,cat_queryset):
        new_name="[merge]"

        old_cats=list(cat_queryset.all())

        for cat in old_cats:
            new_name+=" "+cat.name
        new_cat=self.create(name=new_name)
        children=[]
        for catrel in CategoryRelation.objects.filter(parent__in=old_cats):
            if catrel.child in children:
                catrel.delete()
                continue
            catrel.parent=new_cat
            children.append(catrel.child)
            catrel.save()
        parents=[]
        for catrel in CategoryRelation.objects.filter(child__in=old_cats):
            if new_cat==catrel.parent:
                catrel.delete()
                continue
            if catrel.parent in parents:
                catrel.delete()
                continue
            catrel.child=new_cat
            parents.append(catrel.parent)
            catrel.save()

        L=[]
        for catrel in CategoryTimeSpanRelation.objects.filter(category__in=old_cats):
            if catrel.time_span in L:
                catrel.delete()
                continue
            catrel.category=new_cat
            catrel.save()
            L.append(catrel.time_span)

        L=[]
        for catrel in CategoryPlaceRelation.objects.filter(category__in=old_cats):
            if catrel.place in L:
                catrel.delete()
                continue
            catrel.category=new_cat
            catrel.save()
            L.append(catrel.place)

        L=[]
        for catrel in CategoryPersonRelation.objects.filter(category__in=old_cats):
            if catrel.person in L:
                catrel.delete()
                continue
            catrel.category=new_cat
            catrel.save()
            L.append(catrel.person)

        L=[]
        for catrel in CategoryLanguageRelation.objects.filter(category__in=old_cats):
            if catrel.language in L:
                catrel.delete()
                continue
            catrel.category=new_cat
            catrel.save()
            L.append(catrel.language)

        for cat in old_cats:
            for book in cat.book_set.all():
                book.categories.add(new_cat)
                book.categories.remove(cat)
            cat.delete()

class Category(models.Model):
    name = models.CharField(max_length=4096,unique=True)
    label = models.SlugField(max_length=4096,editable=False,unique=True)
    tree_nodes = GenericRelation(CategoryTreeNode)
    objects = CategoryManager()

    def __str__(self): return str(self.name)

    class Meta:
        ordering = ["name"]
 
    def slugify(self):
        S=str(self.name)
        S=S.replace("#","sharp")
        S=S.replace("++","plusplus")
        return django.template.defaultfilters.slugify(S)

    def save(self, *args, **kwargs):
        self.label = self.slugify()
        super(Category, self).save(*args, **kwargs)

    def parents(self):
        return "; ".join([str(x.parent) for x in self.parent_set.all()])

    def children(self):
        return "; ".join([str(x.child) for x in self.child_set.all()])

    def time_span(self):
        return "; ".join([str(x.time_span) for x in self.categorytimespanrelation_set.all()])

    def place(self):
        return "; ".join([str(x.place) for x in self.categoryplacerelation_set.all()])

    def person(self):
        return "; ".join([str(x.person) for x in self.categorypersonrelation_set.all()])

    def language(self):
        return "; ".join([str(x.language) for x in self.categorylanguagerelation_set.all()])

    def num_books(self):
        return self.book_set.count()

    def min_level(self):
        level=-1
        for node in self.tree_nodes.all():
            if level<0: 
                level=node.level
                continue
            level=min(level,node.level)
        return level

    def num_objects(self):
        node=self.tree_nodes.all().first()
        return node.num_objects

    def my_branch_depth(self):
        node=self.tree_nodes.all().first()
        return node.branch_depth()

    def my_branch_id(self):
        level=-1
        elected=None
        for node in self.tree_nodes.all():
            if level<0: 
                elected=node
                level=node.level
                continue
            if level<=node.level: continue
            elected=node
            level=node.level
        node_id=elected.node_id
        big_parent_id=node_id.split(":")[0]
        #big_parent_node=CategoryTreeNode.objects.get(node_id=big_parent_id)
        return big_parent_id

class CategoryRelation(models.Model):
    child = models.ForeignKey(Category,related_name="parent_set",on_delete=models.PROTECT)
    parent = models.ForeignKey(Category,related_name="child_set",on_delete=models.PROTECT)

    def __str__(self): 
        return str(self.parent)+"/"+str(self.child)

    class Meta:
        ordering = ["parent","child"]

class CategoryTimeSpanRelation(models.Model):
    time_span=models.ForeignKey(TimeSpan,on_delete=models.PROTECT)
    category=models.ForeignKey(Category,on_delete=models.PROTECT)

    def __str__(self):
        return str(self.time_span)+"/"+str(self.category)

class CategoryPlaceRelation(models.Model):
    place=models.ForeignKey(Place,on_delete=models.PROTECT)
    category=models.ForeignKey(Category,on_delete=models.PROTECT)

    def __str__(self):
        return str(self.place)+"/"+str(self.category)

class CategoryPersonRelation(models.Model):
    person=models.ForeignKey(Person,on_delete=models.PROTECT)
    category=models.ForeignKey(Category,on_delete=models.PROTECT)

    def __str__(self):
        return str(self.person)+"/"+str(self.category)

class CategoryLanguageRelation(models.Model):
    language=models.ForeignKey(LanguageVariety,on_delete=models.PROTECT)
    category=models.ForeignKey(Category,on_delete=models.PROTECT)

    def __str__(self):
        return str(self.language)+"/"+str(self.category)

class CategorizedObject(models.Model):
    categories = models.ManyToManyField(Category,blank=True)

    class Meta:
        abstract = True

    def get_categories(self):
        return "; ".join([str(x) for x in self.categories.all()])


### authors

class AuthorManager(PersonManager):

    def catalog(self):

        class CatAuthor(object):
            def __init__(self,db_author):
                self._db_author=db_author
                self.id=db_author.id
                self.list_name=db_author.list_name()
                self.long_name=db_author.long_name()
                self.ordering_name=db_author.ordering_name()
                self.publications=[]

        issues=[ (rel.author,rel.author_role,rel.issue)
                 for rel in IssueAuthorRelation.objects.all().select_related() ]
        books=[ (rel.author,rel.author_role,rel.book)
                for rel in BookAuthorRelation.objects.all().select_related() ]
        articles=[ (rel.author,rel.author_role,rel.article)
                   for rel in ArticleAuthorRelation.objects.all().select_related() ]
        authors=[ CatAuthor(aut) for aut in self.all().select_related().prefetch_related("cache") ]
        dict_aut={ aut.id: aut for aut in authors }

        for aut,role,obj in issues:
            dict_aut[aut.id].publications.append( (obj.year,role,obj) )
        for aut,role,obj in books:
            dict_aut[aut.id].publications.append( (obj.year,role,obj) )
        for aut,role,obj in articles:
            dict_aut[aut.id].publications.append( (obj.year,role,obj) )

        return authors
            
        #return self.all().select_related().prefetch_related("cache","authorrelation_set")

class Author(Person):

    objects=AuthorManager()
    
    class Meta:
        proxy = True

    def publications(self):
        L=[]
        for rel in self.authorrelation_set.all().select_related():
            L.append( (rel.year,rel.author_role,rel.actual()) )
        return L

    def get_absolute_url(self):
        return "/bibliography/author/%d" % self.pk

    def save(self,*args,**kwargs):
        Person.save(self,*args,**kwargs)

class AuthorRole(LabeledAbstract): 
    cover_name = models.BooleanField(default=False)
    action = models.CharField(default="",max_length=1024,blank=True)
    pos = models.IntegerField(unique=True)

class AuthorRelation(models.Model):
    author = models.ForeignKey(Author,on_delete=models.PROTECT)
    author_role = models.ForeignKey(AuthorRole,on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType,editable=False,null=True,on_delete=models.PROTECT)
    year = models.IntegerField(editable=False,db_index=True)
    #year_label = models.CharField(max_length=10,editable=False)

    class Meta:
        ordering = [ "year" ]

    def _year(self): return 0
    def _title(self): return ""

    def html(self): return ""

    def update_year(self):
        try:
            self.year=self.actual()._year()
        except:
            self.year=self._year()
        self.save()

    def actual(self):
        model = self.content_type.model
        return self.__getattribute__(model)

    def save(self,*args, **kwargs):
        if (not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        try:
            self.year=self.actual()._year()
        except:
            self.year=self._year()
        super(AuthorRelation, self).save(*args, **kwargs)

    def clean(self,*args,**kwargs):
        self.year=self._year()
        super(AuthorRelation, self).clean(*args, **kwargs)


class MigrAuthor(models.Model):
    cod = models.CharField(max_length=1,default="-",db_index=True)
    ind = models.IntegerField(db_index=True)
    author = models.ForeignKey(Author,on_delete=models.PROTECT)

    def __str__(self): return str(self.cod)+str(self.ind)+" "+str(self.author)

### publishers

class PublisherState(models.Model):
    name = models.CharField(max_length=4096)

    class Meta:
        ordering = ["name"]

    def __str__(self): return str(self.name)

class PublisherAddress(models.Model):
    city = models.CharField(max_length=4096)
    state = models.ForeignKey(PublisherState,on_delete=models.PROTECT)

    def __str__(self): return str(self.city)+" - "+str(self.state)

    class Meta:
        ordering = ["city"]

class PublisherIsbnManager(models.Manager):
    def isbn_alpha(self):
        return self.all().filter(isbn__iregex=r'^[a-z].*')

    def split_isbn(self,unseparated):
        if not unseparated: return [],[]
        isbn_list=[]
        for isbn in unseparated:
            for n in range(1,9):
                isbn_list.append(isbn[:n])
        L=[ v.isbn for v in self.filter(isbn__in=isbn_list) ]
        if not L:
            return [],unseparated
        uns=[]
        sep=[]
        for isbn in unseparated:
            trovato=False
            for db_isbn in L:
                if isbn.startswith(db_isbn):
                    trovato=True
                    isbn_book=isbn[len(db_isbn):]
                    sep.append( (db_isbn,isbn_book) )
                    break
            if not trovato:
                uns.append(isbn)
        return sep,uns


class PublisherIsbn(models.Model):
    isbn = models.CharField(max_length=4096,unique=True,db_index=True)
    preferred = models.ForeignKey("Publisher",editable=False,blank=True,on_delete=models.PROTECT)
    objects = PublisherIsbnManager()

    class Meta:
        ordering = ["isbn"]

    def update_preferred(self):
        self.preferred=self.get_preferred()
        self.save()

    def get_preferred(self):
        if self._state.adding:
            return Publisher.objects.get(pk=0)
        pubs=list(self.publisher_set.all())
        if len(pubs)!=1:
            for p in pubs:
                if not p.alias:
                    return p
        return pubs[0]

    def clean(self,*args,**kwargs):
        self.preferred=self.get_preferred()
        super(PublisherIsbn, self).clean(*args, **kwargs)

    def save(self,*args,**kwargs):
        self.preferred=self.get_preferred()
        super(PublisherIsbn, self).save(*args, **kwargs)


    def __str__(self): return str(self.isbn)

    def publishers(self):
        return "; ".join(map(str, self.publisher_set.all()))

class PublisherManager(models.Manager):
    def add_prefetch(self,obj_list):
        qset=self.filter(id__in=[obj.id for obj in obj_list])
        qset=qset.prefetch_related("addresses")
        return qset

    def look_for(self,isbn_list):
        qset=PublisherIsbn.objects.filter(isbn__in=isbn_list)
        for pub in qset:
            isbn_list.remove( pub.isbn )
        isbn_ids=[ obj.id for obj in qset ]
        p_qset=self.filter(isbns__id__in=isbn_ids).prefetch_related("isbns","addresses")
        return p_qset,isbn_list

class Publisher(models.Model):
    name = models.CharField(max_length=4096)
    full_name = models.CharField(max_length=4096,blank=True)
    url = models.CharField(max_length=4096,default="--")
    note = models.TextField(blank=True,default="")
    addresses = models.ManyToManyField(PublisherAddress,through='PublisherAddressPublisherRelation',blank=True)
    alias = models.BooleanField(default=False)
    isbns = models.ManyToManyField(PublisherIsbn,blank=True)

    objects=PublisherManager()

    class Meta:
        ordering = ["name"]

    def short_name(self):
        name=self.show_name().lower()
        tname=name.replace(".","").replace(",","").split()
        for s in [ "srl", "spa","editore","editrice","edizioni","verlag","publisher","inc",
                   "éditions","editions","edition","editorial","editori","editoriale","ltd",
                   "gruppo","publishing","yayın","yayınları","co","publications","press","editoriali"]:
            if s in tname:
                tname.remove(s)
        tname=[ s.capitalize() for s in tname ]
        return " ".join(tname)

    def clean(self,*args,**kwargs):
        if not self.full_name:
            self.full_name=self.name
        super(Publisher, self).clean(*args, **kwargs)

    def __str__(self): return str(self.name)

    def address(self):
        return " - ".join([str(x.address.city) for x in self.publisheraddresspublisherrelation_set.order_by("pos")])

    def show_name(self):
        if self.full_name: return self.full_name
        return self.name

    def html(self):
        H=self.name
        adrs=self.address()
        if adrs:
            H+=", "+adrs
        return H

    @cached_property
    def isbn_prefix(self):
        return ", ".join([str(x.isbn) for x in self.isbns.all()])

    @cached_property
    def isbn_list(self):
        return [str(x.isbn) for x in self.isbns.all()]
    

class PublisherAddressPublisherRelation(PositionAbstract):
    address = models.ForeignKey(PublisherAddress,on_delete=models.PROTECT)
    publisher = models.ForeignKey(Publisher,on_delete=models.PROTECT)

    def __str__(self): return str(self.publisher)+" ["+str(self.pos)+"] "+str(self.address)

class MigrPublisherRiviste(models.Model):
    registro = models.CharField(max_length=4096)
    publisher = models.ForeignKey(Publisher,on_delete=models.PROTECT)

    def __str__(self): return str(self.registro)

### publications

class VolumeType(LabeledAbstract): 
    read_as = models.CharField(max_length=1024,default="")

class PublicationManager(models.Manager):
    def issn_alpha(self):
        return self.all().filter(issn_crc='Y')

class Publication(models.Model):
    issn = models.CharField(max_length=128) #7
    issn_crc = models.CharField(max_length=1,editable=False,default="Y")
    publisher = models.ForeignKey(Publisher,on_delete=models.PROTECT)
    title = models.CharField(max_length=4096)
    volume_type = models.ForeignKey(VolumeType,on_delete=models.PROTECT)
    date_format = models.CharField(max_length=4096,default="%Y-%m-%d")

    objects=PublicationManager()
    #periodicity=models.CharField(max_length=128,choices=[ ("monthly","monthly"),("unknown","unknown") ],default="unknown")
    #first_day=models.IntegerField(default=1)

    class Meta:
        ordering = ['title']

    def html(self):
        tit=str(self.title)
        if not tit: return ""
        return "<i>"+tit+"</i>"

    def __str__(self): return str(self.title)

    def get_absolute_url(self):
        return "/bibliography/publication/%d" % self.pk

    def update_crc(self):
        self.issn_crc = self.crc()
        self.save()

    def crc(self):
        if not str(self.issn).isdigit(): return('Y')
        pesi=[8,7,6,5,4,3,2]
        cod_lista=list(map(int,list(self.issn)))
        if len(cod_lista)<7:
            L=len(cod_lista)
            cod_lista+=[0 for x in range(L,7)]
        crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
        if (crc==10): return('X')
        if (crc==11): return(0)
        return(crc)

    def clean(self,*args,**kwargs):
        self.issn_crc = self.crc()
        super(Publication, self).clean(*args, **kwargs)

    def issue_set(self):
        return Issue.objects.filter(volume__publication__id=self.id).order_by("date")

class Volume(models.Model):
    label = models.CharField(max_length=256,db_index=True)
    publication = models.ForeignKey(Publication,on_delete=models.PROTECT)

    def __str__(self): return str(self.publication)+" - "+str(self.label)

    def html(self):
        H=self.publication.html()
        if H:
            H+=", "
        H+=str(self.publication.volume_type.read_as)
        if H:
            H+=" "
        H+=str(self.label)
        return H

### publication issues

class IssueType(LabeledAbstract): pass

class IssueManager(models.Manager):
    def by_publication(self,publication):
        return self.all().filter(volume__publication__id=publication.id).order_by("date")

class Issue(models.Model):
    volume = models.ForeignKey(Volume,on_delete=models.PROTECT)
    issue_type = models.ForeignKey(IssueType,on_delete=models.PROTECT)
    issn_num = models.CharField(max_length=8)
    number = models.CharField(max_length=256)
    title = models.CharField(max_length=4096,blank=True,default="")
    date = models.DateField()
    date_ipotetic = models.BooleanField(default=False)
    html_cache = models.TextField(blank=True,null=True,default="",editable=False)

    authors = models.ManyToManyField(Author,through='IssueAuthorRelation',blank=True)

    objects=IssueManager()

    class Meta:
        ordering = ['date']

    def issn(self):
        return self.volume.publication.issn

    def show_date(self):
        D=self.date.strftime(self.volume.publication.date_format)
        if self.date_ipotetic:
            return D+"?"
        return D

    def save(self,*args,**kwargs):
        self.html_cache=self._html()
        return models.Model.save(self,*args,**kwargs)

    def html(self): return self.html_cache

    def _html(self):
        H=self.volume.html()
        if H:
            H+=", "
        H+="n. "+str(self.number)
        tit=str(self.title)
        if tit:
            H+=", <i>"+tit+"</i>"
        H+=", "
        H+=self.date.strftime("%B %Y")
        if self.date_ipotetic:
            H+="?"
        return H

    def __str__(self):
        U=str(self.volume)
        U+="/"+str(self.number)
        if str(self.title):
            U+=". "+str(self.title)
        return U

    def year(self):
        return self.date.year

class IssueAuthorRelation(AuthorRelation,PositionAbstract):
    issue = models.ForeignKey(Issue,on_delete=models.PROTECT)

    def __str__(self): return str(self.author)+", "+str(self.issue)

    def _year(self): return int(self.issue.year())
    def _title(self): return str(self.issue.title)

    def html(self): 
        print("COM")
        print(self.issue.html())
        return self.issue.html()

    class Meta:
        ordering=["pos"]
        #unique_together= [ 'author','author_role','issue' ]

    def save(self,*args,**kwargs):
        if not self.pos:
            self.pos=1
        return super(IssueAuthorRelation,self).save(*args,**kwargs)

class Article(models.Model):
    title = models.CharField(max_length=4096)
    issue = models.ForeignKey(Issue,on_delete=models.PROTECT)
    page_begin = models.CharField(max_length=10,blank=True,default="x")
    page_end = models.CharField(max_length=10,blank=True,default="x")
    authors = models.ManyToManyField(Author,through='ArticleAuthorRelation',blank=True)
    html_cache = models.TextField(blank=True,null=True,default="",editable=False)

    def get_authors(self):
        return ", ".join([str(x.author.long_name()) for x in self.articleauthorrelation_set.filter(author_role__cover_name=True).order_by("pos")])

    def get_secondary_authors(self):
        L=list(self.articleauthorrelation_set.filter(author_role__cover_name=False).order_by("author_role__pos","pos"))
        ret=""
        curr_pos=-1
        comma=True
        for rel in L:
            if curr_pos!=int(rel.author_role.pos):
                action=str(rel.author_role.action).strip()
                if action:
                    if ret:
                        ret+=", "
                    ret+=action+" "
                    comma=False
                curr_pos=int(rel.author_role.pos)
            if ret and comma: ret+=", "
            ret+=rel.author.long_name()
            comma=True

        return ret


    def __str__(self): return str(self.title) #+" ("+unicode(self.year)+")"

    def issn(self): return self.issue.issn()

    def issn_num(self): return self.issue.issn_num

    def year(self): return self.issue.year()

    def save(self,*args,**kwargs):
        self.html_cache=self._html()
        return models.Model.save(self,*args,**kwargs)

    def html(self): return self.html_cache

    def _html(self):
        H=""
        H+=self.get_authors()
        if H:
            H+=", "
        H+="“"+str(self.title)+"”, "
        sec_authors=self.get_secondary_authors()
        if sec_authors:
            H+=sec_authors+", "
        issue=self.issue.html()
        if issue:
            H+=issue+", "
        if str(self.page_begin)==str(self.page_end):
            H+="p. "+str(self.page_begin)
        else:
            H+="pp. "+str(self.page_begin)+"-"+str(self.page_end)
        return H

class ArticleAuthorRelation(AuthorRelation,PositionAbstract):
    article = models.ForeignKey(Article,on_delete=models.PROTECT)

    def __str__(self): return str(self.author)+", "+str(self.article)

    def _year(self): return int(self.article.year())
    def _title(self): return str(self.article.title)

    def html(self): 
        print("ART")
        print(self.article.html())
        return self.article.html()

    class Meta:
        ordering=["pos"]

### books

class BookManager(models.Manager):
    def isbn_alpha(self):
        return self.all().filter(isbn_crc10='Y').order_by("isbn_ced","isbn_book","year","title")

    def by_isbn_pub(self,isbn):
        print("ISBN:",isbn)
        return self.all().filter(isbn_ced__iexact=isbn).order_by("isbn_ced","isbn_book","year","title")

    def add_prefetch(self,obj_list):
        qset=self.filter(id__in=[book.id for book in obj_list])
        qset=qset.select_related("publisher").prefetch_related("authors")
        return qset

    def look_for(self,isbn_list):
        if not isbn_list: return None,[]
        q=models.Q()
        for isbn_ced,isbn_book in isbn_list:
            q=q|models.Q(isbn_ced=isbn_ced,isbn_book=isbn_book)
        qset=self.filter(q).select_related("publisher").prefetch_related("authors")
        new_isbn_list=[]
        for book in qset:
            isbn_list.remove( (book.isbn_ced,book.isbn_book) )
        return qset,isbn_list
        

class Book(CategorizedObject):
    isbn_ced = models.CharField(max_length=9,db_index=True)
    isbn_book = models.CharField(max_length=9,db_index=True)
    isbn_crc10 = models.CharField(max_length=1,editable=False,default="Y")
    isbn_crc13 = models.CharField(max_length=1,editable=False,default="Y")
    isbn_cache10 = models.CharField(max_length=20,editable=False,default="")
    isbn_cache13 = models.CharField(max_length=20,editable=False,default="")
    title = models.CharField(max_length=4096)
    year = models.IntegerField()
    year_ipotetic = models.BooleanField(default=False)
    publisher = models.ForeignKey(Publisher,on_delete=models.PROTECT)
    authors = models.ManyToManyField(Author,through='BookAuthorRelation',blank=True)

    html_cache = models.TextField(blank=True,default="",editable=False)
    
    objects=BookManager()

    class Meta:
        ordering=["title","year","publisher"]
        index_together=[ ["isbn_ced","isbn_book"] ]


    def get_authors(self):
        return ", ".join([str(x.author.long_name()) for x in self.bookauthorrelation_set.filter(author_role__cover_name=True).order_by("pos")])

    def get_absolute_url(self):
        U="/bibliography/book/%d" % self.pk
        print(U)
        return U

    def get_secondary_authors(self):
        L=list(self.bookauthorrelation_set.filter(author_role__cover_name=False).order_by("author_role__pos","pos"))
        ret=""
        curr_pos=-1
        comma=True
        for rel in L:
            if curr_pos!=int(rel.author_role.pos):
                action=str(rel.author_role.action).strip()
                if action:
                    if ret:
                        ret+=", "
                    ret+=action+" "
                    comma=False
                curr_pos=int(rel.author_role.pos)
            if ret and comma: ret+=", "
            ret+=rel.author.long_name()
            comma=True

        return ret

    def __str__(self): 
        if not self.year_ipotetic:
            return str(self.title)+" ("+str(self.year)+")"
        return str(self.title)+" ("+str(self.year)+"?)"

    @cached_property
    def html(self): return self.html_cache

    def _html(self):
        H=""
        H+=self.get_authors()
        if H:
            H+=", "
        H+="<i>"+str(self.title)+"</i>, "
        sec_authors=self.get_secondary_authors()
        if sec_authors:
            H+=sec_authors+", "
        pub=self.publisher.html()
        if pub:
            H+=pub+", "
        H+=str(self.year)
        if self.year_ipotetic: H+="?"
        return H

    def clean(self,*args,**kwargs):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+str(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+str(self.crc13())
        super(Book, self).clean(*args, **kwargs)

    def save(self,*args,**kwargs):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+str(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+str(self.crc13())
        self.html_cache=self._html()
        super(Book, self).save(*args, **kwargs)

    def update_crc(self):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+str(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+str(self.crc13())
        self.save()

    def isbn10(self):
        return str(self.isbn_ced)+"-"+str(self.isbn_book)+"-"+str(self.isbn_crc10)

    def isbn13(self):
        return "978-"+str(self.isbn_ced)+"-"+str(self.isbn_book)+"-"+str(self.isbn_crc13)

    def crc10(self):
        if not str(self.isbn_book).isdigit(): return('Y')
        if not str(self.isbn_ced).isdigit(): return('Y')
        isbn=str(self.isbn_ced)+str(self.isbn_book)
        pesi=[10,9,8,7,6,5,4,3,2]
        cod_lista=list(map(int,list(isbn)))
        if len(cod_lista)<9:
            L=len(cod_lista)
            cod_lista+=[0 for x in range(L,9)]
        crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
        if (crc==10): return('X')
        if (crc==11): return(0)
        return(crc)

    def crc13(self):
        if not str(self.isbn_book).isdigit(): return('Y')
        if not str(self.isbn_ced).isdigit(): return('Y')
        isbn=str(self.isbn_ced)+str(self.isbn_book)
        pesi=[1,3,1,3,1,3,1,3,1,3,1,3]
        cod_lista=[9,7,8]+list(map(int,list(isbn)))
        if len(cod_lista)<12:
            L=len(cod_lista)
            cod_lista+=[0 for x in range(L,12)]
        crc=10-(sum(map(lambda x,y: x*y,cod_lista,pesi))%10)
        if (crc==10): return(0)
        return(crc)

class BookAuthorRelation(AuthorRelation,PositionAbstract):
    book = models.ForeignKey(Book,on_delete=models.PROTECT)

    def __str__(self): return str(self.author)+", "+str(self.book)

    def _year(self): return int(self.book.year)
    def _title(self): return str(self.book.title)

    def html(self): return self.book.html()
    def get_absolute_url(self): return self.book.get_absolute_url()

    class Meta:
        ordering=["pos"]

class TextsCdrom(LabeledAbstract):
    books = models.ManyToManyField(Book,blank=True)


# class BookTimeSpanRelation(models.Model):
#     time_span=models.ForeignKey(TimeSpan)
#     book=models.OneToOneField(Book)

#     def __str__(self):
#         return unicode(self.time_span)+u"/"+unicode(self.book)

### repository cache

class RepositoryCacheBook(models.Model):
    isbn = models.CharField(max_length=13,unique=True)
    publisher = models.CharField(max_length=4096,default=" ")
    year = models.CharField(max_length=4096,default=" ",blank=True)
    title = models.CharField(max_length=4096,default=" ")
    city = models.CharField(max_length=4096,default=" ")
    indb = models.BooleanField(default=False)

    def clean(self,*args,**kwargs):
        if not self.year:
            self.year=" "
        super(RepositoryCacheBook, self).clean(*args, **kwargs)


    def __str__(self):
        return str(self.isbn)+" "+str(self.title)

    class Meta:
        ordering = [ "isbn" ]

class RepositoryCacheAuthor(PositionAbstract):
    book = models.ForeignKey(RepositoryCacheBook,on_delete=models.PROTECT)
    name = models.CharField(max_length=4096)
    role = models.CharField(max_length=4096)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [ "name" ]


class RepositoryFailedIsbn(models.Model):
    isbn10 = models.CharField(max_length=4096)
    isbn13 = models.CharField(max_length=4096)

    def __str__(self):
        return self.isbn10+"/"+self.isbn13

    class Meta:
        ordering = [ "isbn10" ]
    

### others

class BookSerieWithoutIsbn(models.Model):
    isbn_ced = models.CharField(max_length=9,db_index=True)
    isbn_book_prefix = models.CharField(max_length=9,db_index=True)
    title = models.CharField(max_length=4096)
    title_prefix = models.CharField(max_length=4096,default='',blank=True)
    publisher = models.ForeignKey(Publisher,on_delete=models.PROTECT)
    
    def __str__(self): return str(self.title)

### signals

def category_post_save_handler(sender,instance,created,raw,using,update_fields,**kwargs): 
    if raw: return
    if created:
        CategoryTreeNode.objects.create_category(instance)
    else:
        CategoryTreeNode.objects.update_category(instance)

post_save.connect(category_post_save_handler,sender=Category)

def category_pre_delete_handler(sender,instance,using,**kwargs):
    CategoryTreeNode.objects.remove_category(instance)

pre_delete.connect(category_pre_delete_handler,sender=Category)

class CategoryRelationChangeHandler(object):
    def __init__(self):
        self.old_parents={}
        self.old_children={}

    def pre_save(self,sender,instance,raw,using,update_fields,**kwargs): 
        if raw: return
        if not instance.id: return
        old_obj=CategoryRelation.objects.get(id=instance.id)
        self.old_parents[instance.id]=old_obj.parent
        self.old_children[instance.id]=old_obj.child

    def post_save(self,sender,instance,created,raw,using,update_fields,**kwargs): 
        if raw: return
        if created:
            CategoryTreeNode.objects.add_child_category(instance.parent,instance.child)
            return
        old_parent=None
        old_child=None
        if instance.id in self.old_parents:
            old_parent=self.old_parents[instance.id]
            del(self.old_parents[instance.id])
        if instance.id in self.old_children:
            old_child=self.old_children[instance.id]
            del(self.old_children[instance.id])
        CategoryTreeNode.objects.update_child_category(old_parent,old_child,instance.parent,instance.child)
            
categoryrelation_save_handler=CategoryRelationChangeHandler()

post_save.connect(categoryrelation_save_handler.post_save,sender=CategoryRelation)
pre_save.connect(categoryrelation_save_handler.pre_save,sender=CategoryRelation)

def categoryrelation_pre_delete_handler(sender,instance,using,**kwargs):
    CategoryTreeNode.objects.remove_child_category(instance.parent,instance.child)

pre_delete.connect(categoryrelation_pre_delete_handler,sender=CategoryRelation)

def categorizedobjectcategoryrelation_m2m_changed_handler(sender, instance, action, reverse,model,pk_set,using,**kwargs):

    if action=="post_add":
        function=CategoryTreeNode.objects.add_category_relation
    elif action=="pre_remove":
        function=CategoryTreeNode.objects.remove_category_relation
    else:
        return

    if model==Category:
        cat_list=Category.objects.filter(pk__in=list(pk_set))
        for cat in cat_list: 
            function(cat,instance)
        return

    target_list=model.objects.filter(pk__in=list(pk_set))
    for target in target_list: 
        function(instance,target)

m2m_changed.connect(categorizedobjectcategoryrelation_m2m_changed_handler,sender=Book.categories.through)




# @receiver(django.db.models.signals.m2m_changed, sender=Article.categories.through)
# def modify_articlecategoryrelation_handler(sender, **kwargs):
#     print "Modify",kwargs["instance"],"with action:",kwargs["action"],kwargs["model"],kwargs["pk_set"]


