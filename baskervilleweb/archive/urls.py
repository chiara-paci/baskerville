from django.conf.urls import include, url
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

from . import models,views

app_name="archive"

urlpatterns = [
    url( 
        r'^$',
        TemplateView.as_view(template_name="archive/index.html"),
        name="index" 
    ),

    ## photos

    url( r'^photo/?$',views.PhotoListView.as_view(),name="photo_list" ),
    url( r'^photo/(?P<pk>\d+)/?$',
         DetailView.as_view(model=models.PhotoAsset),
         name="photo_detail" ),
    url( r'^photo/(?P<pk>\d+)\.thumb\.jpeg/?$',
         views.PhotoThumbView.as_view(),name="photo_thumb" ),
    url( r'^photo/(?P<pk>\d+)\.(?P<ext>[^.]*)/?$',
         views.PhotoImageView.as_view(model=models.PhotoAsset),
         name="photo_image" ),

    ## documents

    url( r'^document_asset/(?P<pk>\d+)\.thumb\.jpeg/?$',
         views.DocumentAssetThumbView.as_view(),
         name="document_asset_thumb" ),
    url( r'document/by_label/(?P<slug>\w+)/?$',
         DetailView.as_view(model=models.Document,slug_field="label"),
         name="document_detail_by_label"),
    url( r'document/(?P<pk>\d+)/?$',
         DetailView.as_view(model=models.Document),
         name="document_detail"),
    

]
