from django.conf.urls import include, url
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

from . import models,views

app_name="warehouse"

urlpatterns = [
    # url( r'^$',views.PhotoListView.as_view(),name="index" ),
    url( r'^$',views.IndexView.as_view(),name="index" ),
    url( r'^container/?$',ListView.as_view(model=models.Container),name="container_list" ),
    url( r'^container/(?P<pk>\d+)/?$',
         DetailView.as_view(model=models.Container),
         name="container_detail" ),
    url( r'^container/by_label/(?P<slug>\w+)/?$',
         DetailView.as_view(model=models.Container,slug_field="label"),
         name="container_detail_by_label" ),

    # url( r'^photo/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Photo),name="photo_detail" ),
    # url( r'^photo/(?P<pk>\d+)\.thumb\.jpeg/?$',
    #      views.PhotoThumbView.as_view(),name="photo_thumb" ),
    # url( r'^photo/(?P<pk>\d+)\.(?P<ext>[^.]*)/?$',
    #      views.PhotoImageView.as_view(model=models.Photo),name="photo_image" ),
    # url( r'^document_asset/(?P<pk>\d+)\.thumb\.jpeg/?$',
    #      views.DocumentAssetThumbView.as_view(),name="document_asset_thumb" ),
]
