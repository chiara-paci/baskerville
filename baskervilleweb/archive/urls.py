from django.conf.urls import include, url
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

from . import models,views

app_name="archive"

urlpatterns = [
    url( r'^photo/?$',ListView.as_view(model=models.Photo,paginate_by=100),name="photo_list" ),
    url( r'^photo/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Photo),name="photo_detail" ),
    url( r'^photo/(?P<pk>\d+)\.thumb\.jpeg/?$',views.PhotoThumbView.as_view(),name="photo_thumb" ),
    url( r'^photo/(?P<pk>\d+)\.(?P<ext>[^.]*)/?$',views.PhotoImageView.as_view(model=models.Photo),name="photo_image" ),
]
