from django.shortcuts import render

from django.views.generic import TemplateView

# Create your views here.

from . import models

class IndexView(TemplateView):
    template_name="warehouse/index.html"

    def get_context_data(self,*args,**kwargs):
        ctx=TemplateView.get_context_data(self,*args,**kwargs)
        ctx["roots"]=models.Container.objects.roots()
        return ctx
