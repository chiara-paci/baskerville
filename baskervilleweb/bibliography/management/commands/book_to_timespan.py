#! /usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Book,BookTimeSpanRelation,TimeSpan,DateSystem,DateModifier,TimePoint

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        re_date=re.compile(r'^.*?([0-9]+).*?\-.*?([0-9]+).*?$')
        for book in Book.objects.all():
            title=unicode(book.title)
            if re_date.match(title):
                t=re_date.findall(title)
                print title,t[0]
                # begin,created=TimePoint.objects.get_or_create(date=t[0][0])
                # if created:
                #     print "TP",begin
                # end,created=TimePoint.objects.get_or_create(date=t[0][1])
                # if created:
                #     print "TP",end
                # tspan,created=TimeSpan.objects.get_or_create(begin=begin,end=end)
                # if created:
                #     print "TS",tspan
                # rel,created=BookTimeSpanRelation.objects.get_or_create(book=book,time_span=tspan)
                # if created:
                #     print "CT",rel
