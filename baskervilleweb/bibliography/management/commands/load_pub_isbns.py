#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import Publisher,MigrPublisherRiviste,VolumeType,Pubblication

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load publishers'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=str(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=[x.strip() for x in l.split("%")]
            name=t[0]
            isbn=t[1]
            try:
                ce_obj=Publisher.objects.get(name=name)
            except ObjectDoesNotExist as e:
                print("NE",name)
                continue
            isbn_obj,created=PublisherIsbn.objects.get_or_create(isbn=isbn)
            if created:
                print("CI",isbn_obj)
            ce_obj.isbns.add(isbn_obj)
            ce_obj.save()
                

        fd.close()

