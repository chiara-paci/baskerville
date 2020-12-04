from django.conf.urls import include, url
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

app_name="recipebook"

from . import models

urlpatterns = [
    url( r'^$',ListView.as_view(model=models.RecipeCategory),name="index" ),
    url( r'^recipe/$',ListView.as_view(model=models.RecipeCategory),name="recipecategory_list" ),
    url( r'^recipe/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Recipe),name="recipe_detail" ),
]
