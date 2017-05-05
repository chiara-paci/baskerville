#! /usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Category,CategoryTimeSpanRelation,TimeSpan,DateSystem,DateModifier,TimePoint

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        re_date=re.compile(r'^.*?([0-9]+).*?\-.*?([0-9]+).*?$')
        for cat in Category.objects.all():
            name=unicode(cat.name)
            if re_date.match(name):
                t=re_date.findall(name)
                print name,t[0]
                begin,created=TimePoint.objects.get_or_create(date=t[0][0])
                if created:
                    print "TP",begin
                end,created=TimePoint.objects.get_or_create(date=t[0][1])
                if created:
                    print "TP",end
                tspan,created=TimeSpan.objects.get_or_create(begin=begin,end=end)
                if created:
                    print "TS",tspan
                rel,created=CategoryTimeSpanRelation.objects.get_or_create(category=cat,time_span=tspan)
                if created:
                    print "CT",rel
