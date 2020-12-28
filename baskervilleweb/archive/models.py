from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.functional import cached_property

ARCHIVE_PATH = settings.ARCHIVE_PATH
ARCHIVE_REDIRECT_URL = settings.ARCHIVE_REDIRECT_URL

class ImageFormat(models.Model):
    name = models.CharField(max_length=1024,unique=True)
    description = models.CharField(max_length=8192)

    def __str__(self): 
        if not self.description: return self.name
        return self.description

class MetaLabel(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self): return self.name

class ExifType(models.Model):
    name = models.CharField(max_length=1024)
    exif_id = models.IntegerField(blank=True,default=-1)
    short = models.CharField(max_length=128)
    
    def __str__(self): return self.name

class ExifLabel(models.Model):
    category = models.CharField(max_length=128)
    name = models.CharField(max_length=1024,blank=True)
    type = models.ForeignKey(ExifType,on_delete=models.PROTECT)
    exif_id = models.IntegerField(blank=True,default=-1)

    def __str__(self):
        if self.name: return self.name
        return self.type+" "+str(self.exif_id)

class PhotoDManager(models.Manager):

    def get_years(self):
        return list(map(lambda x: x.year,self.all().dates("datetime","year")))

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('cover')


class PhotoD(models.Model):
    label = models.SlugField(max_length=1024,unique=True)
    description = models.CharField(max_length=8192,blank=True)
    cover = models.ForeignKey('Photo',on_delete=models.PROTECT,blank=True,null=True)
    datetime = models.DateTimeField(default=timezone.now)
    objects=PhotoDManager()

    def __str__(self): return self.label
        
    class Meta:
        ordering = [ "datetime" ]

    def thumb_url(self): return self.cover.thumb_url()
    def image_url(self): return self.cover.image_url()

    def image_redirect_url(self): return self.cover.image_redirect_url()
    def thumb_redirect_url(self): return self.cover.thumb_redirect_url()
        
    #def get_absolute_url(self):
    #    return "/archive/photo/%d/" % (self.cover.id,)

    def albums(self):
        L=list(map(lambda x: x["name"], self.cover.album_set.all().values("name")))
        return ",".join(L)

    @cached_property
    def full_path(self): return self.cover.full_path

    @cached_property
    def thumb_path(self): return self.cover.thumb_path

    @cached_property
    def width(self): return self.cover.width

    @cached_property
    def height(self): return self.cover.height

    @cached_property
    def format(self): return self.cover.format

    @cached_property
    def mode(self): return self.cover.mode

    @cached_property
    def mimetype(self): return self.cover.mimetype


    @cached_property
    def rotated(self): return self.cover.rotated

    @cached_property
    def mirrored(self): return self.cover.mirrored

class PhotoManager(models.Manager):
    def get_years(self):
        return list(map(lambda x: x.year,PhotoD.objects.dates("datetime","year")))

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('photo','format')

class Photo(models.Model):
    photo = models.ForeignKey(PhotoD,on_delete=models.PROTECT,blank=True,null=True)
    full_path =  models.FilePathField(path=ARCHIVE_PATH["photo"]["full"],recursive=True,max_length=1024)
    thumb_path = models.FilePathField(path=ARCHIVE_PATH["photo"]["thumb"],recursive=True,max_length=1024)
    width = models.IntegerField()
    height = models.IntegerField()
    format = models.ForeignKey(ImageFormat,on_delete=models.PROTECT)
    mode = models.CharField(max_length=1024)
    mimetype = models.CharField(max_length=1024)
    rotated = models.CharField(max_length=128, 
                               choices=( ("no","no"),("90 ccw","90 ccw"),
                                         ("90 cw","90 cw"),  ("180","180") ), 
                               default="no")
    mirrored = models.CharField(max_length=128, 
                               choices=( ("no","no"),("horizontal","horizontal"),
                                         ("vertical","vertical") ), 
                               default="no")

    objects=PhotoManager()

    @cached_property
    def description(self): return self.photo.description

    @cached_property
    def datetime(self): return self.photo.datetime

    def albums(self): return self.photo.albums()

    def __str__(self): return self.full_path


    def thumb_url(self):
        return "/archive/photo/%d.thumb.jpeg" % self.id

    def image_url(self):
        t=self.mimetype.split("/")
        return "/archive/photo/%d.%s" % (self.id,t[1])

    def image_redirect_url(self):
        url=self.full_path.replace(ARCHIVE_PATH["photo"]["full"],ARCHIVE_REDIRECT_URL["photo"]["full"])
        return url

    def thumb_redirect_url(self):
        url=self.thumb_path.replace(ARCHIVE_PATH["photo"]["thumb"],ARCHIVE_REDIRECT_URL["photo"]["thumb"])
        return url
        
    def get_absolute_url(self):
        return "/archive/photo/%d/" % (self.id,)

    # def albums(self):
    #     L=list(map(lambda x: x["name"], self.album_set.all().values("name")))
    #     return ",".join(L)
        
    class Meta:
        ordering = [ "photo" ]

class PhotoMetaDatum(models.Model):
    photo = models.ForeignKey(Photo,on_delete=models.PROTECT)
    label = models.ForeignKey(MetaLabel,on_delete=models.PROTECT)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)


class ExifDatum(models.Model):
    photo = models.ForeignKey(Photo,on_delete=models.PROTECT)
    label = models.ForeignKey(ExifLabel,on_delete=models.PROTECT)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.photo)+"/"+str(self.label)

class Album(models.Model):
    name = models.CharField(max_length=1024)
    #photos = models.ManyToManyField(Photo,blank=True)
    dphotos = models.ManyToManyField(PhotoD,blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name

    def photos_count(self):
        return self.dphotos.count()

class Document(models.Model):
    label = models.SlugField(max_length=50,unique=True)
    name = models.CharField(max_length=4096,default="",blank=True)
    
    def __str__(self): return self.name

class DocumentAsset(models.Model):
    document = models.ForeignKey(Document,on_delete=models.CASCADE)
    full_path =  models.FilePathField(path=ARCHIVE_PATH["document_asset"]["full"],recursive=True,max_length=1024)
    thumb_path = models.FilePathField(path=ARCHIVE_PATH["document_asset"]["thumb"],recursive=True,max_length=1024)
    mimetype = models.CharField(max_length=1024)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self): return self.full_path

    def thumb_url(self):
        return "/archive/document_asset/%d.thumb.jpeg" % self.id

    def image_url(self):
        t=self.mimetype.split("/")
        return "/archive/document_asset/%d.%s" % (self.id,t[1])

    def image_redirect_url(self):
        url=self.full_path.replace(ARCHIVE_PATH["document_asset"]["full"],ARCHIVE_REDIRECT_URL["document_asset"]["full"])
        return url

    def thumb_redirect_url(self):
        url=self.thumb_path.replace(
            ARCHIVE_PATH["document_asset"]["thumb"],
            ARCHIVE_REDIRECT_URL["document_asset"]["thumb"]
        )
        return url
        
    def get_absolute_url(self):
        return "/archive/document_asset/%d/" % (self.id,)

    class Meta:
        ordering = [ "full_path" ]

class DocumentCollection(models.Model):
    name = models.CharField(max_length=1024)
    documents = models.ManyToManyField(Document,blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name

    def documents_count(self):
        return self.documents.count()

class DocumentMetaDatum(models.Model):
    document = models.ForeignKey(Document,on_delete=models.PROTECT)
    label = models.ForeignKey(MetaLabel,on_delete=models.PROTECT)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.document)+"/"+str(self.label)

class DocumentAssetMetaDatum(models.Model):
    document_asset = models.ForeignKey(DocumentAsset,on_delete=models.PROTECT)
    label = models.ForeignKey(MetaLabel,on_delete=models.PROTECT)
    value = models.CharField(max_length=8192)

    def __str__(self): return str(self.document_asset)+"/"+str(self.label)
