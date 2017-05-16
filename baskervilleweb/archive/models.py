from django.db import models

# Create your models here.

PHOTO_ARCHIVE_FULL = "/home/chiara/foto/full"
PHOTO_ARCHIVE_THUMB = "/home/chiara/foto/thumb"

class ImageFormat(models.Model):
    name = models.CharField(max_length=1024,unique=True)
    description = models.CharField(max_length=8192)

    def __str__(self): return self.name

class Photo(models.Model):
    full_path =  models.FilePathField(path=PHOTO_ARCHIVE_FULL,recursive=True,max_length=1024)
    thumb_path = models.FilePathField(path=PHOTO_ARCHIVE_THUMB,recursive=True,max_length=1024)
    description = models.CharField(max_length=8192,blank=True)
    width = models.IntegerField()
    height = models.IntegerField()
    format = models.ForeignKey(ImageFormat)
    mode = models.CharField(max_length=1024)

    type = models.CharField(max_length=1024)

    def __str__(self): return self.full_path

class MetaLabel(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self): return self.name

class PhotoMetaDatum(models.Model):
    photo = models.ForeignKey(Photo)
    label = models.ForeignKey(MetaLabel)
    value = models.CharField(max_length=1024)

    def __str__(self): return str(self.phot)+"/"+str(self.label)

