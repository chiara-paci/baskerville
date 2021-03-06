from django.shortcuts import render
from django.views.generic import DetailView,ListView
from django.http import HttpResponse

# Create your views here.

from . import models
from PIL import Image
import os.path

from django.conf import settings


# class ImageMixin(object):
#     def adjust_photo(self,img,photo):
#         if photo.rotated=="no": return img
#         if photo.rotated=="180": 
#             return img.rotate(180)
#         if photo.rotated=="90 cw":
#             return img.rotate(-90,expand=True)
#         return img.rotate(90,expand=True)

# class PhotoImageView(DetailView):
#     model = models.Photo

#     def get(self,request,*args,**kwargs):
#         photo=self.get_object()
#         response = HttpResponse()
#         #response["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(photo.image_url()))
#         response["Content-Type"]=""
#         response['X-Accel-Redirect'] = photo.image_redirect_url()
#         return response

# class PhotoThumbView(DetailView):
#     model = models.Photo

#     def get(self,request,*args,**kwargs):
#         photo=self.get_object()
#         response = HttpResponse()
#         #response["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(photo.thumb_url()))
#         response["Content-Type"]=""
#         response['X-Accel-Redirect'] = photo.thumb_redirect_url()
#         return response

class PhotoImageView(DetailView):
    model = models.PhotoAsset

    def get_image_format(self,ext):
        if ext in [ "jpg", "jpeg" ]: return "image/jpeg","JPEG"
        if ext in ["png","gif","tiff"]: 
            return "image/%s" % ext,ext.upper()
        return None,None

    def get(self,request,*args,**kwargs):
        photo=self.get_object()
        if not settings.ARCHIVE_TEST:
            response = HttpResponse()
            #response["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(photo.image_url()))
            response["Content-Type"]=""
            response['X-Accel-Redirect'] = photo.image_redirect_url()
            return response

        ext=kwargs["ext"].lower()
        mimetype,savetype=self.get_image_format(ext)
        img=Image.open(photo.full_path)
        if not mimetype: mimetype=photo.mimetype
        response = HttpResponse(content_type=mimetype)
        if savetype:
            img.save(response, savetype)
        else:
            img.save(response)
        img.close()
        return response

class PhotoThumbView(DetailView):
    model = models.PhotoAsset

    def get_image_format(self):
        mimetype="image/jpeg"
        savetype="JPEG"
        return mimetype,savetype

    def get(self,request,*args,**kwargs):
        photo=self.get_object()
        if not settings.ARCHIVE_TEST:
            response = HttpResponse()
            #response["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(photo.thumb_url()))
            response["Content-Type"]=""
            response['X-Accel-Redirect'] = photo.thumb_redirect_url()
            return response
        img=Image.open(photo.thumb_path)
        mimetype,savetype=self.get_image_format()
        response = HttpResponse(content_type=mimetype)
        img.save(response, savetype)
        img.close()
        return response

class DocumentAssetThumbView(DetailView):
    model = models.DocumentAsset

    def get_image_format(self):
        mimetype="image/jpeg"
        savetype="JPEG"
        return mimetype,savetype

    def get(self,request,*args,**kwargs):
        asset=self.get_object()
        if not settings.ARCHIVE_TEST:
            response = HttpResponse()
            #response["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(asset.thumb_url()))
            response["Content-Type"]=""
            response['X-Accel-Redirect'] = asset.thumb_redirect_url()
            return response
        img=Image.open(asset.thumb_path)
        mimetype,savetype=self.get_image_format()
        response = HttpResponse(content_type=mimetype)
        img.save(response, savetype)
        img.close()
        return response

class Filter(object):

    def __init__(self,name,q_name):
        self.name=name
        self.q_name=q_name

    def empty(self,querydict):
        querydict=querydict.copy()
        if self.q_name not in querydict:
            return ("All",True,querydict.urlencode())
        vals=querydict.pop(self.q_name)
        return ("All",False,querydict.urlencode())

    def values(self): return []

    def to_param(self,x): return str(x)

    def to_label(self,x): return str(x)

    def get_params(self,querydict):
        querydict=querydict.copy()
        if "page" in querydict:
            querydict.pop("page")
        ret=[self.empty(querydict)]
        if self.q_name in querydict:
            selected=querydict.pop(self.q_name)
        else:
            selected=[]
        base_q=querydict.urlencode()

        if base_q:
            def f(x):
                return "&".join([base_q,"%s=%s" % (self.q_name,self.to_param(x))])
        else:
            def f(x):
                return "%s=%s" % (self.q_name,self.to_param(x))

        for x in self.values():
            if self.to_param(x) in selected:
                ret.append( (self.to_label(x),True,f(x)) )
            else:
                ret.append( (self.to_label(x),False,f(x)) )
        return ret

    def apply_filter(self,selected,queryset):
        return queryset

    def filter_qset(self,querydict,queryset):
        if not self.q_name in querydict:
            return queryset
        selected=querydict.getlist(self.q_name)
        return self.apply_filter(selected,queryset)

class FieldFilter(Filter):
    def __init__(self,field):
        Filter.__init__(self,field,field)
        self.field=field

    def values(self):
        return list(map(lambda x: x[self.field],
                        models.PhotoAsset.objects.all().values(self.field).order_by(self.field).distinct()))

    def apply_filter(self,selected,queryset):
        kwargs={
            self.field+"__in": selected
        }
        return queryset.filter(**kwargs)

class YearFilter(Filter):
    def __init__(self):
        Filter.__init__(self,"year","year")

    def values(self): 
        return models.PhotoAsset.objects.get_years()

    def apply_filter(self,selected,queryset):
        return queryset.filter(datetime__year__in=selected)

class AlbumFilter(Filter):
    def __init__(self):
        Filter.__init__(self,"album","album")

    def to_param(self,x): return str(x.id)

    def values(self): 
        return models.Album.objects.all()

    def apply_filter(self,selected,queryset):
        return queryset.filter(album__id__in=selected)

class PhotoYearFilter(Filter):
    def __init__(self):
        Filter.__init__(self,"year","year")

    def values(self): 
        return models.PhotoAsset.objects.get_years()

    def apply_filter(self,selected,queryset):
        return queryset.filter(photo__datetime__year__in=selected)

class PhotoAlbumFilter(Filter):
    def __init__(self):
        Filter.__init__(self,"album","album")

    def to_param(self,x): return str(x.id)

    def values(self): 
        return models.Album.objects.all()

    def apply_filter(self,selected,queryset):
        return queryset.filter(photo__album__id__in=selected)

class PhotoListView(ListView):
    model=models.PhotoAsset
    paginate_by=100

    filter_list=[
        PhotoAlbumFilter(),
        #AlbumFilter(),
        #YearFilter(),
        PhotoYearFilter(),
        FieldFilter("width"),
        FieldFilter("height"),
        FieldFilter("mimetype"),
    ]

    def get_queryset(self,*args,**kwargs):
        qset=ListView.get_queryset(self,*args,**kwargs)
        for f in self.filter_list:
            qset=f.filter_qset(self.request.GET,qset)
        return qset

    def get_context_data(self,*args,**kwargs):
        ctx=ListView.get_context_data(self,*args,**kwargs)
        # ret=[ (str(x),False,"year="+str(x)) for x in models.PhotoAsset.objects.get_years() ]
        ctx["filter_list"]=[]
        for f in self.filter_list:
            ctx["filter_list"].append({
                "name": f.name,
                "params": f.get_params(self.request.GET)
            })
        qcopy=self.request.GET.copy()
        if "page" in qcopy:
            qcopy.pop("page")
        ctx["parameters"]=qcopy.urlencode()
        return ctx
        
