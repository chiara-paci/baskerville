#! /usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from bibliography.models import TimePoint,CategoryTimeSpanRelation

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        for cts in CategoryTimeSpanRelation.objects.filter(category__name__istartswith="opere "):
            cat_name=str(cts.category).strip()
            t=cat_name.split(" ")
            x=t[-1].split("-")
            if len(x)<=1:
                print(cts.category,len(x),"<====================================")
                continue
            print(cts.category,":",x[0],x[1])
            b=int(x[0])
            e=int(x[1])
            cts.time_span.begin.date=b
            cts.time_span.end.date=e
            cts.time_span.begin.save()
            cts.time_span.end.save()
            cts.category.name=cat_name
            cts.category.save()
            ts_name=cat_name.replace("opere ","vita ")
            cts.time_span.name=ts_name
            cts.time_span.save()
            print("    ",cts.time_span,cts.time_span.begin,cts.time_span.end)
