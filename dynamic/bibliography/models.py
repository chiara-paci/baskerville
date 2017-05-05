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
        if model_dict["model_label"] in [ "article","articleauthorrelation","issuetype","issue","publication","volumetype","volume" ]:
            ret["Publication"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "nameformat","nametype","nameformatcollection","personcache",
                                          "person","personnamerelation" ]:
            ret["Person"].append(model_dict)
            continue
        if model_dict["model_label"] in [ "categorytreenode","category","categoryrelation",
                                          "categorytimespanrelation", "categoryplacerelation", "categorypersonrelation", 
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

    def __unicode__(self):
        return unicode(self.label)

    def clean(self,*args,**kwargs):
        self.label = self.label.lower()
        super(LabeledAbstract, self).clean(*args, **kwargs)

### time span

class DateModifier(PositionAbstract):
    name = models.CharField(max_length=1024)
    reverse = models.BooleanField(default=False)

    class Meta:
        ordering = [ 'pos' ]

    def __unicode__(self):
        if self.id==0: return ""
        if not self.name: return "-"
        return unicode(self.name)

    def save(self,*args,**kwargs):
        super(DateModifier, self).save(*args, **kwargs)
        for obj in self.timepoint_set.all():
            obj.save()

class TimePoint(models.Model):
    date = models.IntegerField()
    modifier = models.ForeignKey(DateModifier,blank=True,default=0)

    class Meta:
        ordering = [ 'modifier','date' ]
        unique_together= [ 'modifier','date' ]

    def __unicode__(self):
        U=unicode(abs(self.date))
        if self.modifier.id!=0:
            U+=" "+unicode(self.modifier)
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
        return u"; ".join(map(lambda x: unicode(x),self.begin_set.all()))
        
    def ends(self):
        return u"; ".join(map(lambda x: unicode(x),self.end_set.all()))
        
    def time_spans(self):
        L=map(lambda x: unicode(x),self.begin_set.all())
        L+=map(lambda x: unicode(x),self.end_set.all())
        L=list(set(L))
        return "; ".join(L)

class TimeSpan(models.Model):
    begin = models.ForeignKey(TimePoint,related_name="begin_set")
    end   = models.ForeignKey(TimePoint,related_name="end_set")
    name  = models.CharField(max_length=4096,blank=True)

    def __unicode__(self):
        if self.name:
            return unicode(self.name)
        return unicode(self.begin)+"-"+unicode(self.end)

    class Meta:
        ordering = [ 'begin','end' ]

    def categories(self):
        return u"; ".join(map(lambda x: unicode(x.category),self.categorytimespanrelation_set.all()))


### language

class Language(models.Model):
    name = models.CharField(max_length=4096)

    def __unicode__(self): return self.name

    def families(self):
        return u"; ".join(map(lambda x: unicode(x.family),self.languagefamilyrelation_set.all()))

    def varieties(self):
        return u"; ".join(map(lambda x: unicode(x),self.languagevariety_set.all()))

class LanguageFamily(models.Model):
    name = models.CharField(max_length=4096)

    def __unicode__(self): return self.name

    def parents(self):
        return u"; ".join(map(lambda x: unicode(x.parent),self.parent_set.all()))

    def children(self):
        return u"; ".join(map(lambda x: unicode(x.child),self.child_set.all()))

    def languages(self):
        return u"; ".join(map(lambda x: unicode(x.language),self.languagefamilyrelation_set.all()))

class LanguageFamilyRelation(models.Model):
    language = models.ForeignKey(Language)
    family = models.ForeignKey(LanguageFamily)

    def __unicode__(self): 
        return unicode(self.family)+u"/"+unicode(self.language)

class LanguageFamilyFamilyRelation(models.Model):
    parent = models.ForeignKey(LanguageFamily,related_name="child_set")
    child = models.ForeignKey(LanguageFamily,related_name="parent_set")

    def __unicode__(self): 
        return unicode(self.parent)+u"/"+unicode(self.child)

    class Meta:
        ordering = ["parent","child"]
    
    
class LanguageVarietyType(models.Model):
    name = models.CharField(max_length=4096)    

    def __unicode__(self): return self.name

class LanguageVariety(models.Model):
    name = models.CharField(max_length=4096,blank=True)
    language = models.ForeignKey(Language)
    type = models.ForeignKey(LanguageVarietyType,default=1)

    def __unicode__(self):
        if self.type.id==1:
            return unicode(self.language)
        if not self.name:
            return unicode(self.language)
        return unicode(self.language)+" ("+unicode(self.name)+")"

### place

class PlaceType(models.Model):
    name = models.CharField(max_length=4096)

    def __unicode__(self): return self.name

class Place(models.Model):
    name = models.CharField(max_length=4096,unique=True)
    type = models.ForeignKey(PlaceType)

    def __unicode__(self):
        return self.name

    def alternate_names(self):
        return u"; ".join(map(lambda x: unicode(x.name),self.alternateplacename_set.all()))

    def areas(self):
        return u"; ".join(map(lambda x: unicode(x.area),self.area_set.all()))

    def places(self):
        return u"; ".join(map(lambda x: unicode(x.place),self.place_set.all()))

    class Meta:
        ordering = [ "name" ]

class AlternatePlaceName(models.Model):
    place = models.ForeignKey(Place)
    name = models.CharField(max_length=4096)
    note = models.CharField(max_length=65536,blank=True)

    def __unicode__(self):
        return self.name

class PlaceRelation(models.Model):
    place = models.ForeignKey(Place,related_name="area_set")
    area = models.ForeignKey(Place,related_name="place_set")

    def __unicode__(self): 
        return unicode(self.area)+u"/"+unicode(self.place)

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
    long_format = models.ForeignKey(NameFormat,related_name='long_format_set')
    short_format = models.ForeignKey(NameFormat,related_name='short_format_set')
    list_format = models.ForeignKey(NameFormat,related_name='list_format_set')
    ordering_format = models.ForeignKey(NameFormat,related_name='ordering_format_set')

    preferred = models.BooleanField(default=False)

    objects = NameFormatCollectionManager()

    def save(self, *args, **kwargs):
        super(NameFormatCollection, self).save(*args, **kwargs)
        for person in self.person_set.all():
            person.update_cache()

    @cached_property
    def fields(self):
        L=["name","surname"]
        long_name=unicode(self.long_format.pattern)
        short_name=unicode(self.short_format.pattern)
        list_name=unicode(self.list_format.pattern)
        ordering_name=unicode(self.ordering_format.pattern)

        for s in "VALURNIC":
            long_name=long_name.replace("{{"+s+"|","{{")
            short_name=short_name.replace("{{"+s+"|","{{")
            list_name=list_name.replace("{{"+s+"|","{{")
            ordering_name=ordering_name.replace("{{"+s+"|","{{")
        
        names=[]
        for f in [long_name,short_name,list_name,ordering_name]:
            L=map(lambda x: x.replace("{{","").replace("}}",""),
                  re.findall(r'{{.*?}}',f))
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
        long_name=unicode(self.long_format.pattern)
        short_name=unicode(self.short_format.pattern)
        list_name=unicode(self.list_format.pattern)
        ordering_name=unicode(self.ordering_format.pattern)
        for key,val in names.items():
            val_f={}
            t=RE_NAME_SEP.split(val)
            #t=map(lambda x: x.capitalize(),RE_NAME_SEP.split(val))
            vons_t=[]
            norm_t=[]
            for x in t:
                if x.lower() in VONS:
                    vons_t.append(x.lower())
                else:
                    if len(x)==1 and x.isalpha():
                        vons_t.append(x+".")
                    else:
                        vons_t.append(x)
                if len(x)==1 and x.isalpha():
                    norm_t.append(x+".")
                else:
                    norm_t.append(x)
                    
            cap_t=map(lambda x: x.capitalize(),norm_t)
            val_norm="".join(norm_t)
            val_f["L"]=val.lower()
            val_f["U"]=val.upper()
            val_f["N"]=val.lower().replace(" ","_")
            val_f["I"]=". ".join(map(lambda x: x[0].upper(),filter(bool,val.split(" "))))+"."
            val_f["C"]="".join(cap_t)
            val_f["V"]="".join(vons_t)

            if val.isdigit():
                val_f["R"]=ROMANS[int(val)-1]
                val_f["A"]="%3.3d" % int(val)
            else:
                val_f["R"]=""
                val_f["A"]=""

            long_name=long_name.replace("{{"+key+"}}",val_norm)
            short_name=short_name.replace("{{"+key+"}}",val_norm)
            list_name=list_name.replace("{{"+key+"}}",val_norm)
            ordering_name=ordering_name.replace("{{"+key+"}}",val_norm)

            for k in "VALURNIC":
                long_name=long_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                short_name=short_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                list_name=list_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                ordering_name=ordering_name.replace("{{"+k+"|"+key+"}}",val_f[k])

        return long_name,short_name,list_name,ordering_name

class PersonCache(models.Model):
    long_name = models.CharField(max_length=4096,default="-")
    short_name = models.CharField(max_length=4096,default="-")
    list_name = models.CharField(max_length=4096,default="-")
    ordering_name = models.CharField(max_length=4096,default="-")

    class Meta:
        ordering = ["ordering_name"]
        db_table = 'bibliography_personcache'

    def __unicode__(self): return self.list_name

class PersonManager(models.Manager):

    def search_names(self,names):
        qset=self.all()
        if len(names)==0: return qset
        D=[]
        for name in names:
            if name.endswith("."):
                name=name[:-1]
                S=set(map(lambda x: x.person.id,PersonNameRelation.objects.filter(value__istartswith=name)))
            elif len(name)==1:
                S=set(map(lambda x: x.person.id,PersonNameRelation.objects.filter(value__istartswith=name)))
            else:
                S=set(map(lambda x: x.person.id,PersonNameRelation.objects.filter(value__iexact=name)))
            D.append(S)
        for id_set in D:
            qset=qset.filter(id__in=list(id_set))
        if qset.count()>0: return qset
        if len(names)==1: return qset
        if len(names)==2:
            newnames=[ " ".join(names) ]
            return self.search_names(newnames)
        L=len(names)
        for n in range(0,L-1):
            newnames=names[0:n] + [ " ".join(names[n:n+2])] + names[n+2:L]
            qset=self.search_names(newnames)
            if qset.count()>0: return qset
        return qset
        
    
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

    def create_by_names(self,format_collection,**kwargs):
        obj=self.create(format_collection=format_collection)
        for key,val in kwargs.items():
            name_type,created=NameType.objects.get_or_create(label=key)
            rel,created=PersonNameRelation.objects.get_or_create(person=obj,name_type=name_type,
                                                                 defaults={"value": val})
            if not created:
                rel.value=val
                rel.save()
        return obj


class Person(models.Model):
    format_collection = models.ForeignKey(NameFormatCollection)
    cache = models.OneToOneField(PersonCache,editable=False,null=True)
    names = models.ManyToManyField(NameType,through='PersonNameRelation',blank=True)

    objects = PersonManager()

    class Meta:
        ordering = ["cache"]
        db_table = 'bibliography_person'

    def __unicode__(self):
        return self.list_name()

    def long_name(self): return unicode(self.cache.long_name)
    def short_name(self): return unicode(self.cache.short_name)
    def ordering_name(self): return unicode(self.cache.ordering_name)
    def list_name(self): return unicode(self.cache.list_name)

    def save(self, *args, **kwargs):
        if not self.cache:
            self.cache = PersonCache.objects.create()
        super(Person, self).save(*args, **kwargs)
        self.update_cache()

    def update_cache(self):
        names={}
        for rel in self.personnamerelation_set.all():
            names[unicode(rel.name_type.label)]=unicode(rel.value)
        long_name,short_name,list_name,ordering_name=self.format_collection.apply_formats(names)
        self.cache.long_name = long_name
        self.cache.short_name = short_name
        self.cache.list_name = list_name
        self.cache.ordering_name = ordering_name
        self.cache.save()

class PersonNameRelation(models.Model):
    person = models.ForeignKey(Person)
    name_type = models.ForeignKey(NameType)
    value = models.CharField(max_length=4096,default="-")

    def __unicode__(self): return unicode(self.value)

    def save(self, *args, **kwargs):
        super(PersonNameRelation, self).save(*args, **kwargs)
        self.person.update_cache()

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
            return self.filter(level=level,node_id__istartswith=base_node.node_id+u":")
        return self.filter(level=level,node_id__istartswith=base_node.node_id+u":",is_category=True)

    def update_category(self,cat): 
        ctype = ContentType.objects.get_for_model(Category)
        for cat_node in self.filter(content_type=ctype,object_id=cat.id):
            level=int(cat_node.level)
            old_node_id=unicode(cat_node.node_id)
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
        old_node_id=unicode(cat_node.node_id)
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
            new_cch_node_id=unicode(cch_node.node_id).replace(old_node_id+":",new_node_id+":",1)
            new_cch_level=int(cch_node.level)-old_level+new_level
            cch_node.node_id=new_cch_node_id
            cch_node.level=new_cch_level
            cch_node.save()
            ret.append(("R",cch_node))

        return ret

    def clone(self,parent_node_id,parent_level,cat_node):
        ret=[]
        old_node_id=unicode(cat_node.node_id)
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
            new_cch_node_id=unicode(cch_node.node_id).replace(old_node_id+":",new_node_id+":",1)
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
            new_objects=self.reparent(unicode(fn.node_id),int(fn.level),cn)
            startind=1
            fn.has_children=True
            fn.save()

        for fn in parent_nodes[startind:]:
            new_objects+=self.clone(unicode(fn.node_id),int(fn.level),cn)
            fn.has_children=True
            fn.save()

        return new_objects

    def remove_child_category(self,parent,child): 
        parent_nodes=list(parent.tree_nodes.all())
        child_nodes=list(child.tree_nodes.all())

        del_list=[]
        
        for fn in parent_nodes:
            fn_node_id=unicode(fn.node_id)
            for cn in child_nodes:
                cn_node_id=unicode(cn.node_id)
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
            parent.has_children=bool(self.filter(node_id__istartswith=unicode(parent.node_id)+":").exists())
            parent.save()

    def update_child_category(self,old_parent,old_child,new_parent,new_child):
        if not old_parent and not old_child: return
        if (old_parent==new_parent) and (old_child==new_child): return
        self.remove_child_category(old_parent,old_child)
        self.add_child_category(new_parent,new_child)

    def remove_branch(self,basenode):
        base_node_id=unicode(basenode.node_id)
        self.filter(node_id__istartswith=base_node_id+":").delete()
        self.filter(node_id=base_node_id).delete()

    def add_category_relation(self,cat,child):
        parent_nodes=list(cat.tree_nodes.all())

        ret=[]
        for fn in parent_nodes:
            new_node_id=unicode(fn.node_id)+":"+unicode(child.id)
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
            node_ids.append(unicode(fn.node_id)+":"+unicode(child.id))
        self.filter(node_id__in=node_ids).delete()

        for fn in parent_nodes:
            fn.has_children=bool(self.filter(node_id__istartswith=unicode(fn.node_id)+":").exists())
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
    content_type = models.ForeignKey(ContentType)
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
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",level=level,is_category=True).count()
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",level=level).count()
        
    def branch(self,only_cat=True):
        if only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",is_category=True)
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":")

    def __unicode__(self):
        U= u"%3d %s" % (int(self.level),unicode(self.node_id))
        return U

    def direct_size(self):
        if not self.is_category: return 0
        return self.content_object.child_set.count()

    class Meta:
        ordering = [ "node_id" ]

    def save(self, *args, **kwargs):
        self.label_children="_"+unicode(self.node_id).replace(":","_")
        t=unicode(self.node_id).split(":")
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
                    children_ids+=map(lambda x: x.object_id,list(L))
                children_ids=list(set(children_ids))
                return self.filter(id__in=children_ids)
        return CategoryQueryset(Category)

    def query_set_branch(self,queryset,parent_id):
        parent=Category.objects.get(id=int(parent_id))
        children_ids=[parent.id]
        for catnode in parent.tree_nodes.all():
            L=catnode.branch()
            children_ids+=map(lambda x: x.object_id,list(L))
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

    def __unicode__(self): return unicode(self.name)

    class Meta:
        ordering = ["name"]
 
    def slugify(self):
        S=unicode(self.name)
        S=S.replace("#","sharp")
        S=S.replace("++","plusplus")
        return django.template.defaultfilters.slugify(S)

    def save(self, *args, **kwargs):
        self.label = self.slugify()
        super(Category, self).save(*args, **kwargs)

    def parents(self):
        return u"; ".join(map(lambda x: unicode(x.parent),self.parent_set.all()))

    def children(self):
        return u"; ".join(map(lambda x: unicode(x.child),self.child_set.all()))

    def time_span(self):
        return u"; ".join(map(lambda x: unicode(x.time_span),self.categorytimespanrelation_set.all()))

    def place(self):
        return u"; ".join(map(lambda x: unicode(x.place),self.categoryplacerelation_set.all()))

    def person(self):
        return u"; ".join(map(lambda x: unicode(x.person),self.categorypersonrelation_set.all()))

    def language(self):
        return u"; ".join(map(lambda x: unicode(x.language),self.categorylanguagerelation_set.all()))

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
    child = models.ForeignKey(Category,related_name="parent_set")
    parent = models.ForeignKey(Category,related_name="child_set")

    def __unicode__(self): 
        return unicode(self.parent)+u"/"+unicode(self.child)

    class Meta:
        ordering = ["parent","child"]

class CategoryTimeSpanRelation(models.Model):
    time_span=models.ForeignKey(TimeSpan)
    category=models.ForeignKey(Category)

    def __unicode__(self):
        return unicode(self.time_span)+u"/"+unicode(self.category)

class CategoryPlaceRelation(models.Model):
    place=models.ForeignKey(Place)
    category=models.ForeignKey(Category)

    def __unicode__(self):
        return unicode(self.place)+u"/"+unicode(self.category)

class CategoryPersonRelation(models.Model):
    person=models.ForeignKey(Person)
    category=models.ForeignKey(Category)

    def __unicode__(self):
        return unicode(self.person)+u"/"+unicode(self.category)

class CategoryLanguageRelation(models.Model):
    language=models.ForeignKey(LanguageVariety)
    category=models.ForeignKey(Category)

    def __unicode__(self):
        return unicode(self.language)+u"/"+unicode(self.category)

class CategorizedObject(models.Model):
    categories = models.ManyToManyField(Category,blank=True)

    class Meta:
        abstract = True

    def get_categories(self):
        return "; ".join(map(lambda x: unicode(x),self.categories.all()))


### authors

class Author(Person):
    class Meta:
        proxy = True

    def publications(self):
        L=[]
        for rel in self.authorrelation_set.all():
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
    author = models.ForeignKey(Author)
    author_role = models.ForeignKey(AuthorRole)
    content_type = models.ForeignKey(ContentType,editable=False,null=True)
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
    author = models.ForeignKey(Author)

    def __unicode__(self): return unicode(self.cod)+unicode(self.ind)+u" "+unicode(self.author)

### publishers

class PublisherState(models.Model):
    name = models.CharField(max_length=4096)

    class Meta:
        ordering = ["name"]

    def __unicode__(self): return unicode(self.name)

class PublisherAddress(models.Model):
    city = models.CharField(max_length=4096)
    state = models.ForeignKey(PublisherState)

    def __unicode__(self): return unicode(self.city)+u" - "+unicode(self.state)

    class Meta:
        ordering = ["city"]

class PublisherIsbnManager(models.Manager):
    def isbn_alpha(self):
        return self.all().filter(isbn__iregex=r'^[a-z].*')

class PublisherIsbn(models.Model):
    isbn = models.CharField(max_length=4096,unique=True)
    preferred = models.ForeignKey("Publisher",editable=False,blank=True)
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

    def __unicode__(self): return unicode(self.isbn)

    def publishers(self):
        return "; ".join(map(unicode, self.publisher_set.all()))

class Publisher(models.Model):
    name = models.CharField(max_length=4096)
    full_name = models.CharField(max_length=4096,blank=True)
    url = models.CharField(max_length=4096,default="--")
    note = models.TextField(blank=True,default="")
    addresses = models.ManyToManyField(PublisherAddress,through='PublisherAddressPublisherRelation',blank=True)
    alias = models.BooleanField(default=False)
    isbns = models.ManyToManyField(PublisherIsbn,blank=True)

    class Meta:
        ordering = ["name"]

    def clean(self,*args,**kwargs):
        if not self.full_name:
            self.full_name=self.name
        super(Publisher, self).clean(*args, **kwargs)

    def __unicode__(self): return unicode(self.name)

    def address(self):
        return " - ".join(map(lambda x: unicode(x.address.city),self.publisheraddresspublisherrelation_set.order_by("pos")))

    def show_name(self):
        if self.full_name: return self.full_name
        return self.name

    def html(self):
        H=self.name
        adrs=self.address()
        if adrs:
            H+=", "+adrs
        return H

    def isbn_prefix(self):
        return ", ".join(map(lambda x: unicode(x.isbn),self.isbns.all()))

class PublisherAddressPublisherRelation(PositionAbstract):
    address = models.ForeignKey(PublisherAddress)
    publisher = models.ForeignKey(Publisher)

    def __unicode__(self): return unicode(self.publisher)+u" ["+unicode(self.pos)+u"] "+unicode(self.address)

class MigrPublisherRiviste(models.Model):
    registro = models.CharField(max_length=4096)
    publisher = models.ForeignKey(Publisher)

    def __unicode__(self): return unicode(self.registro)

### publications

class VolumeType(LabeledAbstract): 
    read_as = models.CharField(max_length=1024,default="")

class PublicationManager(models.Manager):
    def issn_alpha(self):
        return self.all().filter(issn_crc='Y')

class Publication(models.Model):
    issn = models.CharField(max_length=128) #7
    issn_crc = models.CharField(max_length=1,editable=False,default="Y")
    publisher = models.ForeignKey(Publisher)
    title = models.CharField(max_length=4096)
    volume_type = models.ForeignKey(VolumeType)
    date_format = models.CharField(max_length=4096,default="%Y-%m-%d")

    objects=PublicationManager()
    #periodicity=models.CharField(max_length=128,choices=[ ("monthly","monthly"),("unknown","unknown") ],default="unknown")
    #first_day=models.IntegerField(default=1)

    class Meta:
        ordering = ['title']

    def html(self):
        tit=unicode(self.title)
        if not tit: return ""
        return "<i>"+tit+"</i>"

    def __unicode__(self): return unicode(self.title)

    def get_absolute_url(self):
        return "/bibliography/publication/%d" % self.pk

    def update_crc(self):
        self.issn_crc = self.crc()
        self.save()

    def crc(self):
        if not unicode(self.issn).isdigit(): return('Y')
        pesi=[8,7,6,5,4,3,2]
        cod_lista=map(int,list(self.issn))
        if len(cod_lista)<7:
            L=len(cod_lista)
            cod_lista+=map(lambda x: 0, range(L,7))
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
    publication = models.ForeignKey(Publication)

    def __unicode__(self): return unicode(self.publication)+u" - "+unicode(self.label)

    def html(self):
        H=self.publication.html()
        if H:
            H+=", "
        H+=unicode(self.publication.volume_type.read_as)
        if H:
            H+=" "
        H+=unicode(self.label)
        return H

### publication issues

class IssueType(LabeledAbstract): pass

class IssueManager(models.Manager):
    def by_publication(self,publication):
        return self.all().filter(volume__publication__id=publication.id).order_by("date")

class Issue(models.Model):
    volume = models.ForeignKey(Volume)
    issue_type = models.ForeignKey(IssueType)
    issn_num = models.CharField(max_length=8)
    number = models.CharField(max_length=256)
    title = models.CharField(max_length=4096,blank=True,default="")
    date = models.DateField()
    authors = models.ManyToManyField(Author,through='IssueAuthorRelation',blank=True)

    objects=IssueManager()

    class Meta:
        ordering = ['date']

    def issn(self):
        return self.volume.publication.issn

    def show_date(self):
        return self.date.strftime(self.volume.publication.date_format)

    def html(self):
        H=self.volume.html()
        if H:
            H+=", "
        H+="n. "+unicode(self.number)
        tit=unicode(self.title)
        if tit:
            H+=", <i>"+tit+"</i>"
        H+=", "
        H+=self.date.strftime("%B %Y")
        return H

    def __unicode__(self):
        U=unicode(self.volume)
        U+=u"/"+unicode(self.number)
        if unicode(self.title):
            U+=u". "+unicode(self.title)
        return U

    def year(self):
        return self.date.year

class IssueAuthorRelation(AuthorRelation,PositionAbstract):
    issue = models.ForeignKey(Issue)

    def __unicode__(self): return unicode(self.author)+u", "+unicode(self.issue)

    def _year(self): return int(self.issue.year())
    def _title(self): return unicode(self.issue.title)

    def html(self): 
        print "COM"
        print self.issue.html()
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
    issue = models.ForeignKey(Issue)
    page_begin = models.CharField(max_length=10,blank=True,default="x")
    page_end = models.CharField(max_length=10,blank=True,default="x")
    authors = models.ManyToManyField(Author,through='ArticleAuthorRelation',blank=True)

    def get_authors(self):
        return ", ".join(map(lambda x: unicode(x.author.long_name()), 
                             self.articleauthorrelation_set.filter(author_role__cover_name=True).order_by("pos")))

    def get_secondary_authors(self):
        L=list(self.articleauthorrelation_set.filter(author_role__cover_name=False).order_by("author_role__pos","pos"))
        ret=""
        curr_pos=-1
        comma=True
        for rel in L:
            if curr_pos!=int(rel.author_role.pos):
                action=unicode(rel.author_role.action).strip()
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


    def __unicode__(self): return unicode(self.title) #+" ("+unicode(self.year)+")"

    def issn(self): return self.issue.issn()

    def issn_num(self): return self.issue.issn_num

    def year(self): return self.issue.year()

    def html(self):
        H=""
        H+=self.get_authors()
        if H:
            H+=", "
        H+=u"“"+unicode(self.title)+u"”, "
        sec_authors=self.get_secondary_authors()
        if sec_authors:
            H+=sec_authors+", "
        issue=self.issue.html()
        if issue:
            H+=issue+", "
        if unicode(self.page_begin)==unicode(self.page_end):
            H+="p. "+unicode(self.page_begin)
        else:
            H+="pp. "+unicode(self.page_begin)+"-"+unicode(self.page_end)
        return H

class ArticleAuthorRelation(AuthorRelation,PositionAbstract):
    article = models.ForeignKey(Article)

    def __unicode__(self): return unicode(self.author)+u", "+unicode(self.article)

    def _year(self): return int(self.article.year())
    def _title(self): return unicode(self.article.title)

    def html(self): 
        print "ART"
        print self.article.html()
        return self.article.html()

    class Meta:
        ordering=["pos"]

### books

class BookManager(models.Manager):
    def isbn_alpha(self):
        return self.all().filter(isbn_crc10='Y').order_by("isbn_ced","isbn_book","year","title")

class Book(CategorizedObject):
    isbn_ced = models.CharField(max_length=9,db_index=True)
    isbn_book = models.CharField(max_length=9,db_index=True)
    isbn_crc10 = models.CharField(max_length=1,editable=False,default="Y")
    isbn_crc13 = models.CharField(max_length=1,editable=False,default="Y")
    isbn_cache10 = models.CharField(max_length=20,editable=False,default="")
    isbn_cache13 = models.CharField(max_length=20,editable=False,default="")
    title = models.CharField(max_length=4096)
    year = models.IntegerField()
    publisher = models.ForeignKey(Publisher)
    authors = models.ManyToManyField(Author,through='BookAuthorRelation',blank=True)

    objects=BookManager()

    def get_authors(self):
        return ", ".join(map(lambda x: unicode(x.author.long_name()), 
                             self.bookauthorrelation_set.filter(author_role__cover_name=True).order_by("pos")))

    def get_absolute_url(self):
        U=u"/bibliography/book/%d" % self.pk
        print U
        return U

    def get_secondary_authors(self):
        L=list(self.bookauthorrelation_set.filter(author_role__cover_name=False).order_by("author_role__pos","pos"))
        ret=""
        curr_pos=-1
        comma=True
        for rel in L:
            if curr_pos!=int(rel.author_role.pos):
                action=unicode(rel.author_role.action).strip()
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

    class Meta:
        ordering=["title","year","publisher"]

    def __unicode__(self): return unicode(self.title)+u" ("+unicode(self.year)+u")"

    def html(self):
        H=""
        H+=self.get_authors()
        if H:
            H+=", "
        H+="<i>"+unicode(self.title)+"</i>, "
        sec_authors=self.get_secondary_authors()
        if sec_authors:
            H+=sec_authors+", "
        pub=self.publisher.html()
        if pub:
            H+=pub+", "
        H+=unicode(self.year)
        return H

    def clean(self,*args,**kwargs):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+unicode(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+unicode(self.crc13())
        super(Book, self).clean(*args, **kwargs)

    def save(self,*args,**kwargs):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+unicode(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+unicode(self.crc13())
        super(Book, self).save(*args, **kwargs)

    def update_crc(self):
        self.isbn_crc10 = self.crc10()
        self.isbn_crc13 = self.crc13()
        self.isbn_cache10=self.isbn_ced+self.isbn_book+unicode(self.crc10())
        self.isbn_cache13='978'+self.isbn_ced+self.isbn_book+unicode(self.crc13())
        self.save()

    def isbn10(self):
        return unicode(self.isbn_ced)+"-"+unicode(self.isbn_book)+"-"+unicode(self.isbn_crc10)

    def isbn13(self):
        return "978-"+unicode(self.isbn_ced)+"-"+unicode(self.isbn_book)+"-"+unicode(self.isbn_crc13)

    def crc10(self):
        if not unicode(self.isbn_book).isdigit(): return('Y')
        if not unicode(self.isbn_ced).isdigit(): return('Y')
        isbn=unicode(self.isbn_ced)+unicode(self.isbn_book)
        pesi=[10,9,8,7,6,5,4,3,2]
        cod_lista=map(int,list(isbn))
        if len(cod_lista)<9:
            L=len(cod_lista)
            cod_lista+=map(lambda x: 0, range(L,9))
        crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
        if (crc==10): return('X')
        if (crc==11): return(0)
        return(crc)

    def crc13(self):
        if not unicode(self.isbn_book).isdigit(): return('Y')
        if not unicode(self.isbn_ced).isdigit(): return('Y')
        isbn=unicode(self.isbn_ced)+unicode(self.isbn_book)
        pesi=[1,3,1,3,1,3,1,3,1,3,1,3]
        cod_lista=[9,7,8]+map(int,list(isbn))
        if len(cod_lista)<12:
            L=len(cod_lista)
            cod_lista+=map(lambda x: 0, range(L,12))
        crc=10-(sum(map(lambda x,y: x*y,cod_lista,pesi))%10)
        if (crc==10): return(0)
        return(crc)

class BookAuthorRelation(AuthorRelation,PositionAbstract):
    book = models.ForeignKey(Book)

    def __unicode__(self): return unicode(self.author)+u", "+unicode(self.book)

    def _year(self): return int(self.book.year)
    def _title(self): return unicode(self.book.title)

    def html(self): return self.book.html()
    def get_absolute_url(self): return self.book.get_absolute_url()

    class Meta:
        ordering=["pos"]

class TextsCdrom(LabeledAbstract):
    books = models.ManyToManyField(Book,blank=True)


# class BookTimeSpanRelation(models.Model):
#     time_span=models.ForeignKey(TimeSpan)
#     book=models.OneToOneField(Book)

#     def __unicode__(self):
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


    def __unicode__(self):
        return unicode(self.isbn)+u" "+unicode(self.title)

    class Meta:
        ordering = [ "isbn" ]

class RepositoryCacheAuthor(PositionAbstract):
    book = models.ForeignKey(RepositoryCacheBook)
    name = models.CharField(max_length=4096)
    role = models.CharField(max_length=4096)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = [ "name" ]


class RepositoryFailedIsbn(models.Model):
    isbn10 = models.CharField(max_length=4096)
    isbn13 = models.CharField(max_length=4096)

    def __unicode__(self):
        return self.isbn10+"/"+self.isbn13

    class Meta:
        ordering = [ "isbn10" ]
    

### others

class BookSerieWithoutIsbn(models.Model):
    isbn_ced = models.CharField(max_length=9,db_index=True)
    isbn_book_prefix = models.CharField(max_length=9,db_index=True)
    title = models.CharField(max_length=4096)
    title_prefix = models.CharField(max_length=4096,default='',blank=True)
    publisher = models.ForeignKey(Publisher)
    
    def __unicode__(self): return unicode(self.title)


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
        if self.old_parents.has_key(instance.id):
            old_parent=self.old_parents[instance.id]
            del(self.old_parents[instance.id])
        if self.old_children.has_key(instance.id):
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


