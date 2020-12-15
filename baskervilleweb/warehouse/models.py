from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.

class ContainerType(models.Model):
    name = models.CharField(max_length=1024,unique=True)

    def __str__(self): return self.name
    
class Container(models.Model):
    label = models.SlugField(max_length=50,unique=True)
    description = models.CharField(max_length=8192)
    type = models.ForeignKey(ContainerType,on_delete=models.PROTECT)

    def __str__(self): return self.label

class ObjectContainerRelation(models.Model):
    container = models.ForeignKey(Container,on_delete=models.PROTECT,related_name="item_set")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')    

    def __str__(self): return "%s/%s" % (str(self.container),str(self.item))

