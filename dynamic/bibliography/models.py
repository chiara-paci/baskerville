# -*- coding: utf-8 -*-

from django.db import models
import django.template.defaultfilters
from django.db.models import Max

# Create your models here.

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals
from django.dispatch import receiver

from santaclara_base.models import PositionAbstract

import re

RE_NAME_SEP=re.compile("('| |-)")

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

class DateSystem(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return unicode(self.name)

class DateModifier(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return unicode(self.name)

class TimePoint(models.Model):
    date = models.CharField(max_length=1024)
    system = models.ForeignKey(DateSystem,blank=True,default=0)
    modifier = models.ForeignKey(DateModifier,blank=True,default=0)

    def __unicode__(self):
        U=u""
        if self.modifier.id!=0:
            U+=unicode(self.modifier)+" "
        U+=unicode(self.date)
        if self.system.id!=0:
            U+=" "+unicode(self.system)
        return U

    def save(self,*args,**kwargs):
        if not self.system:
            self.system=DateSystem.objects.get(id=0)
        if not self.modifier:
            self.modifier=DateModifier.objects.get(id=0)
        super(TimePoint, self).save(*args, **kwargs)

class TimeSpan(models.Model):
    begin = models.ForeignKey(TimePoint,related_name="begin_set")
    end   = models.ForeignKey(TimePoint,related_name="end_set")
    name  = models.CharField(max_length=4096,blank=True)

    def __unicode__(self):
        if self.name:
            return unicode(self.name)
        return unicode(self.begin)+"-"+unicode(self.end)

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

    def add_child_category(self,father,child):
        print "Add",child,"to",father

        father_nodes=list(father.tree_nodes.all())
        child_nodes=list(child.tree_nodes.all())

        cn=child_nodes[0]
        startind=0
        new_objects=[]
        if len(child_nodes)==1 and child_nodes[0].level==0:
            ## l'unico child è un rootnode
            fn=father_nodes[0]
            new_objects=self.reparent(unicode(fn.node_id),int(fn.level),cn)
            startind=1
            fn.has_children=True
            fn.save()

        for fn in father_nodes[startind:]:
            new_objects+=self.clone(unicode(fn.node_id),int(fn.level),cn)
            fn.has_children=True
            fn.save()

        return new_objects

    def remove_child_category(self,father,child): 
        father_nodes=list(father.tree_nodes.all())
        child_nodes=list(child.tree_nodes.all())

        del_list=[]
        
        for fn in father_nodes:
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

        for father,node in del_list:
            self.remove_branch(node)
            father.has_children=bool(self.filter(node_id__istartswith=unicode(father.node_id)+":").exists())
            father.save()

    def remove_branch(self,basenode):
        base_node_id=unicode(basenode.node_id)
        self.filter(node_id__istartswith=base_node_id+":").delete()
        self.filter(node_id=base_node_id).delete()

    def add_category_relation(self,cat,child):
        father_nodes=list(cat.tree_nodes.all())

        ret=[]
        for fn in father_nodes:
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

    def remove_category_relation(self,cat,child): pass

    def get_num_objects(self,catnode):
        if not catnode.is_category: return 1
        N=self.filter(node_id__istartswith=catnode.node_id+":",is_category=False).values("content_type","object_id").distinct().count()
        print catnode,N
        return N

    def max_level(self,only_cat=True):
        if not only_cat:
            return self.all().aggregate(Max('level'))["level__max"]
        return self.filter(is_category=True).aggregate(Max('level'))["level__max"]

class CategoryTreeNode(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

    node_id = models.CharField(max_length=4096,unique=True)
    has_children = models.BooleanField()
    level = models.PositiveIntegerField()
    objects = CategoryTreeNodeManager()

    label = models.CharField(max_length=4096,editable=False)
    label_children = models.CharField(max_length=4096,editable=False)
    is_category = models.BooleanField(editable=False)

    num_objects = models.PositiveIntegerField(editable=False)

    def branch_depth(self,only_cat=True):
        if not only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":").aggregate(Max('level'))["level__max"]
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",is_category=True).aggregate(Max('level'))["level__max"]

    def branch_level_size(self,level,only_cat=True):
        if not only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",level=level).count()
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",level=level,is_category=True).count()
        
    def branch(self,only_cat=True):
        if not only_cat:
            return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":")
        return CategoryTreeNode.objects.filter(node_id__istartswith=self.node_id+":",is_category=True)

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
            def all_in_branch(self,father_id):
                father=Category.objects.get(id=int(father_id))
                children_ids=[]
                for catnode in father.tree_nodes.all():
                    L=catnode.branch()
                    children_ids+=map(lambda x: x.object_id,list(L))
                children_ids=list(set(children_ids))
                return self.filter(id__in=children_ids)
        return CategoryQueryset(Category)

    def all_in_branch(self,father_id):
        return self.get_query_set().all_in_branch(father_id)

class Category(models.Model):
    name = models.CharField(max_length=4096,unique=True)
    label = models.SlugField(max_length=4096,editable=False,unique=True)
    tree_nodes = generic.GenericRelation(CategoryTreeNode)
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

    def fathers(self):
        return u"; ".join(map(lambda x: unicode(x.father),self.father_set.all()))

    def children(self):
        return u"; ".join(map(lambda x: unicode(x.child),self.child_set.all()))

    def min_level(self):
        level=-1
        for node in self.tree_nodes.all():
            if level<0: 
                level=node.level
                continue
            level=min(level,node.level)
        return level

    def num_objects(self):
        # un modo meno becero?
        for node in self.tree_nodes.all():
            return node.num_objects

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
    child = models.ForeignKey(Category,related_name="father_set")
    father = models.ForeignKey(Category,related_name="child_set")

    def __unicode__(self): 
        return unicode(self.father)+u"/"+unicode(self.child)

    class Meta:
        ordering = ["father","child"]

class CategoryTimeSpanRelation(models.Model):
    time_span=models.ForeignKey(TimeSpan)
    category=models.ForeignKey(Category,unique=True)

    def __unicode__(self):
        return unicode(self.time_span)+u"/"+unicode(self.category)


class CategorizedObject(models.Model):
    categories = models.ManyToManyField(Category,blank=True)

    class Meta:
        abstract = True

    def get_categories(self):
        return "; ".join(map(lambda x: unicode(x),self.categories.all()))

### authors

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

class NameFormatCollection(LabeledAbstract):
    long_format = models.ForeignKey(NameFormat,related_name='long_format_set')
    short_format = models.ForeignKey(NameFormat,related_name='short_format_set')
    list_format = models.ForeignKey(NameFormat,related_name='list_format_set')
    ordering_format = models.ForeignKey(NameFormat,related_name='ordering_format_set')

    def save(self, *args, **kwargs):
        super(NameFormatCollection, self).save(*args, **kwargs)
        for author in self.author_set.all():
            author.update_cache()

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
        vons=["von","di","da","del","della","dell","dello","dei","degli","delle","de","d",
              "dal","dalla","dall","dallo","dai","dagli","dalle","al","ibn"]
        romans=["I","II","III","IV","V","VI","VII","VIII","IX","X",
                "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX",
                "XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII","XXIX","XXX",
                "XXXI","XXXII","XXXIII","XXXIV","XXXV","XXXVI","XXXVII","XXXVIII","XXXIX","XL",
                "XLI","XLII","XLIII","XLIV","XLV","XLVI","XLVII","XLVIII","XLIX","L"]

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
                if x.lower() in vons:
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
                val_f["R"]=romans[int(val)-1]
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

class AuthorCache(models.Model):
    long_name = models.CharField(max_length=4096,default="-")
    short_name = models.CharField(max_length=4096,default="-")
    list_name = models.CharField(max_length=4096,default="-")
    ordering_name = models.CharField(max_length=4096,default="-")

    class Meta:
        ordering = ["ordering_name"]

class Author(models.Model):
    format_collection = models.ForeignKey(NameFormatCollection)
    cache = models.OneToOneField(AuthorCache,editable=False,null=True)
    names = models.ManyToManyField(NameType,through='AuthorNameRelation',blank=True)

    class Meta:
        ordering = ["cache"]

    def __unicode__(self):
        return self.list_name()

    def long_name(self): return unicode(self.cache.long_name)
    def short_name(self): return unicode(self.cache.short_name)
    def ordering_name(self): return unicode(self.cache.ordering_name)
    def list_name(self): return unicode(self.cache.list_name)

    def save(self, *args, **kwargs):
        if (not self.cache):
            self.cache = AuthorCache.objects.create()
        super(Author, self).save(*args, **kwargs)
        self.update_cache()

    def update_cache(self):
        names={}
        for rel in self.authornamerelation_set.all():
            names[unicode(rel.name_type.label)]=unicode(rel.value)
        long_name,short_name,list_name,ordering_name=self.format_collection.apply_formats(names)
        self.cache.long_name = long_name
        self.cache.short_name = short_name
        self.cache.list_name = list_name
        self.cache.ordering_name = ordering_name
        self.cache.save()

    def publications(self):
        L=[]
        for rel in self.authorrelation_set.all():
            L.append( (rel.year,rel.author_role,rel.actual()) )
        return L

class AuthorNameRelation(models.Model):
    author = models.ForeignKey(Author)
    name_type = models.ForeignKey(NameType)
    value = models.CharField(max_length=4096,default="-")

    def __unicode__(self): return unicode(self.value)

    def save(self, *args, **kwargs):
        super(AuthorNameRelation, self).save(*args, **kwargs)
        self.author.update_cache()

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

class PublisherIsbn(models.Model):
    isbn = models.CharField(max_length=4096,unique=True)
    preferred = models.ForeignKey("Publisher",editable=False,blank=True)

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

class Publication(models.Model):
    issn = models.CharField(max_length=128)
    issn_crc = models.CharField(max_length=1,editable=False,default="Y")
    publisher = models.ForeignKey(Publisher)
    title = models.CharField(max_length=4096)
    volume_type = models.ForeignKey(VolumeType)

    class Meta:
        ordering = ['title']

    def html(self):
        tit=unicode(self.title)
        if not tit: return ""
        return "<i>"+tit+"</i>"

    def __unicode__(self): return unicode(self.title)

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

class Issue(models.Model):
    volume = models.ForeignKey(Volume)
    issue_type = models.ForeignKey(IssueType)
    issn_num = models.CharField(max_length=8)
    number = models.CharField(max_length=256)
    title = models.CharField(max_length=4096,blank=True,default="")
    date = models.DateField()

    def issn(self):
        return self.volume.publication.issn

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

    def get_authors(self):
        return ", ".join(map(lambda x: unicode(x.author.long_name()), 
                             self.bookauthorrelation_set.filter(author_role__cover_name=True).order_by("pos")))

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

    class Meta:
        ordering=["pos"]

class TextsCdrom(LabeledAbstract):
    books = models.ManyToManyField(Book,blank=True)


class BookTimeSpanRelation(models.Model):
    time_span=models.ForeignKey(TimeSpan)
    book=models.ForeignKey(Book,unique=True)

    def __unicode__(self):
        return unicode(self.time_span)+u"/"+unicode(self.book)

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

@receiver(django.db.models.signals.post_save, sender=Category)
def create_category_handler(sender, **kwargs):
    if kwargs["raw"]: return
    cat=kwargs["instance"]
    if kwargs["created"]:
        CategoryTreeNode.objects.create_category(cat)
    else:
        CategoryTreeNode.objects.update_category(cat)

@receiver(django.db.models.signals.post_save, sender=CategoryRelation)
def create_categoryrelation_handler(sender, **kwargs):
    if not kwargs["created"]: return
    if kwargs["raw"]: return
    catrel=kwargs["instance"]
    CategoryTreeNode.objects.add_child_category(catrel.father,catrel.child)

@receiver(django.db.models.signals.pre_delete, sender=CategoryRelation)
def remove_categoryrelation_handler(sender, **kwargs):
    catrel=kwargs["instance"]
    CategoryTreeNode.objects.remove_child_category(catrel.father,catrel.child)

def modify_categorizedobjectcategoryrelation_handler(sender, **kwargs):
    if kwargs["action"]=="post_add":
        function=CategoryTreeNode.objects.add_category_relation
    elif kwargs["action"]=="pre_remove":
        function=CategoryTreeNode.objects.remove_category_relation
    else:
        return

    if kwargs["model"]==Category:
        target=kwargs["instance"]
        cat_list=Category.objects.filter(pk__in=list(kwargs["pk_set"]))
        for cat in cat_list: 
            function(cat,target)
        return

    cat=kwargs["instance"]
    target_list=kwargs["model"].objects.filter(pk__in=list(kwargs["pk_set"]))
    for target in target_list: 
        function(cat,target)

        
from django.db.models.signals import m2m_changed

m2m_changed.connect(modify_categorizedobjectcategoryrelation_handler,sender=Book.categories.through)



# @receiver(django.db.models.signals.m2m_changed, sender=Article.categories.through)
# def modify_articlecategoryrelation_handler(sender, **kwargs):
#     print "Modify",kwargs["instance"],"with action:",kwargs["action"],kwargs["model"],kwargs["pk_set"]


