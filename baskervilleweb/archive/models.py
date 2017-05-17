from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.

PHOTO_ARCHIVE_FULL = settings.PHOTO_ARCHIVE_FULL
PHOTO_ARCHIVE_THUMB = settings.PHOTO_ARCHIVE_THUMB

class ImageFormat(models.Model):
    name = models.CharField(max_length=1024,unique=True)
    description = models.CharField(max_length=8192)

    def __str__(self): 
        if not self.description: return self.name
        return self.description

class PhotoManager(models.Manager):
    def get_years(self):
        return list(map(lambda x: x.year,self.all().dates("datetime","year")))

class Photo(models.Model):
    full_path =  models.FilePathField(path=PHOTO_ARCHIVE_FULL,recursive=True,max_length=1024)
    thumb_path = models.FilePathField(path=PHOTO_ARCHIVE_THUMB,recursive=True,max_length=1024)
    description = models.CharField(max_length=8192,blank=True)
    width = models.IntegerField()
    height = models.IntegerField()
    format = models.ForeignKey(ImageFormat)
    mode = models.CharField(max_length=1024)
    mimetype = models.CharField(max_length=1024)
    datetime = models.DateTimeField(default=timezone.now)
    rotated = models.CharField(max_length=128, 
                               choices=( ("no","no"),("90 ccw","90 ccw"),
                                         ("90 cw","90 cw"),  ("180","180") ), 
                               default="no")
    mirrored = models.CharField(max_length=128, 
                               choices=( ("no","no"),("horizontal","horizontal"),
                                         ("vertical","vertical") ), 
                               default="no")

    objects=PhotoManager()

    def __str__(self): return self.full_path

    def thumb_url(self):
        return "/archive/photo/%d.thumb.jpeg" % self.id

    def image_url(self):
        t=self.mimetype.split("/")
        return "/archive/photo/%d.%s" % (self.id,t[1])
        
    def get_absolute_url(self):
        return "/archive/photo/%d/" % (self.id,)

    def albums(self):
        L=list(map(lambda x: x["name"], self.album_set.all().values("name")))
        return ",".join(L)
        

    class Meta:
        ordering = [ "datetime" ]

class MetaLabel(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self): return self.name

class PhotoMetaDatum(models.Model):
    photo = models.ForeignKey(Photo)
    label = models.ForeignKey(MetaLabel)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)

class ExifType(models.Model):
    name = models.CharField(max_length=1024)
    exif_id = models.IntegerField(blank=True,default=-1)
    short = models.CharField(max_length=128)
    
    def __str__(self): return self.name

class ExifLabel(models.Model):
    category = models.CharField(max_length=128)
    name = models.CharField(max_length=1024,blank=True)
    type = models.ForeignKey(ExifType)
    exif_id = models.IntegerField(blank=True,default=-1)

    def __str__(self):
        if self.name: return self.name
        return self.type+" "+str(self.exif_id)

class ExifDatum(models.Model):
    photo = models.ForeignKey(Photo)
    label = models.ForeignKey(ExifLabel)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)


class Album(models.Model):
    name = models.CharField(max_length=1024)
    photos = models.ManyToManyField(Photo,blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name

    def photos_count(self):
        return self.photos.count()
