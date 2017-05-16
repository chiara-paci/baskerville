from django.shortcuts import render
from django.views.generic import DetailView
from django.http import HttpResponse

# Create your views here.

from . import models
from PIL import Image

class ImageMixin(object):
    def adjust_photo(self,img,photo):
        if photo.rotated=="no": return img
        if photo.rotated=="180": 
            return img.rotate(180)
        if photo.rotated=="90 cw":
            return img.rotate(-90,expand=True)
        return img.rotate(90,expand=True)

class PhotoImageView(DetailView,ImageMixin):
    model = models.Photo
    
    def get_image_format(self,ext):
        if ext in [ "jpg", "jpeg" ]: return "image/jpeg","JPEG"
        if ext in ["png","gif","tiff"]: 
            return "image/%s" % ext,ext.upper()
        return None,None

    def get(self,request,*args,**kwargs):
        photo=self.get_object()
        ext=kwargs["ext"].lower()
        mimetype,savetype=self.get_image_format(ext)
        img=Image.open(photo.full_path)
        new_img=self.adjust_photo(img,photo)

        if not mimetype: mimetype=photo.mimetype
        response = HttpResponse(content_type=mimetype)
        if savetype:
            new_img.save(response, savetype)
        else:
            new_img.save(response)
        img.close()
        return response

class PhotoThumbView(DetailView,ImageMixin):
    model = models.Photo
    

    def get_image_format(self):
        mimetype="image/jpeg"
        savetype="JPEG"
        return mimetype,savetype

    def get(self,request,*args,**kwargs):
        photo=self.get_object()
        img=Image.open(photo.thumb_path)
        mimetype,savetype=self.get_image_format()
        new_img=self.adjust_photo(img,photo)
        response = HttpResponse(content_type=mimetype)
        new_img.save(response, savetype)
        img.close()
        return response


