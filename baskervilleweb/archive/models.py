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

    mimetype = models.CharField(max_length=1024)

    def __str__(self): return self.full_path

class MetaLabel(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self): return self.name

class PhotoMetaDatum(models.Model):
    photo = models.ForeignKey(Photo)
    label = models.ForeignKey(MetaLabel)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)

class ExifLabel(models.Model):
    exif_id = models.IntegerField()
    type = models.CharField(max_length=128,choices=( ("tag","tag"), ("gps","gps") ) )
    name = models.CharField(max_length=1024,blank=True)

    def __str__(self):
        if self.name: return self.name
        return self.type+" "+str(self.exif_id)

class ExifDatum(models.Model):
    photo = models.ForeignKey(Photo)
    label = models.ForeignKey(ExifLabel)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)


