from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count,F,Q

from bibliography import models

class Command(BaseCommand):

    def add_arguments(self, parser): pass
        # parser.add_argument('passwd')
        # parser.add_argument('--num',type=int,default=4)

    def handle(self, *args, **options):
        olist=list(models.Book.objects.all())+list(models.Issue.objects.all())+list(models.Article.objects.all())
        L=len(olist)
        n=1
        for obj in olist:
            obj.save()
            if not n%100:
                print( "%d/%d %s" % (n,L,obj.html_cache) )
            n+=1
        
