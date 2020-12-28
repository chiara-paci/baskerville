from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property


# Create your models here.

class ContainerType(models.Model):
    name = models.CharField(max_length=1024,unique=True)

    def __str__(self): return self.name

class ContainedMixin(object):

    @cached_property
    def container(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            container = Container.objects.get(
                content_type__pk = ctype.id, 
                object_id=self.id
            )
        except Container.DoesNotExist:
            return None 
        return container

class ContainerManager(models.Manager):
    def roots(self): 
        ctype = ContentType.objects.get_for_model(Container)
        rqset=ObjectContainerRelation.objects.filter(content_type=ctype)
        pk_list=rqset.values("object_id")
        
        return self.all().exclude(pk__in=pk_list)

    
class Container(ContainedMixin,models.Model):
    label = models.SlugField(max_length=50,unique=True)
    description = models.CharField(max_length=8192)
    type = models.ForeignKey(ContainerType,on_delete=models.PROTECT)
    objects = ContainerManager()

    def __str__(self): return self.label

    def children(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        return [ rel.item for rel in self.item_set.filter(content_type=ctype)]

    def items(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        return [ rel.item for rel in self.item_set.exclude(content_type=ctype)]

    def get_absolute_url(self):
        return "/warehouse/container/%d" % self.pk

            

class ObjectContainerRelation(models.Model):
    container = models.ForeignKey(Container,on_delete=models.PROTECT,
                                  related_name="item_set")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')    

    def __str__(self): return "%s/%s" % (str(self.container),str(self.item))

    class Meta:
         unique_together = ('content_type', 'object_id',)
