from django.conf.urls import include, url
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

app_name="home"

urlpatterns = [
    url( r'^$',TemplateView.as_view(template_name="home/index.html"),name="home_index" ),
]
