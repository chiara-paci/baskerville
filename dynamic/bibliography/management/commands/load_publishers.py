#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import PublisherAddress,Publisher,PublisherAddressPublisherRelation

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load publishers'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=map(lambda x: x.strip(),l.split("%"))
            name=t[0]
            url=t[1]
            city=t[2]
            pos=t[3]
            note=t[4]
            try:
                city_obj=PublisherAddress.objects.get(city=city)
            except ObjectDoesNotExist, e:
                print "NE",city
                continue
            ce_obj,created=Publisher.objects.get_or_create(name=name,url=url,note=note)
            if created:
                print "CE",ce_obj
            rel,created=PublisherAddressPublisherRelation.objects.get_or_create(pos=pos,publisher=ce_obj,address=city_obj)
            if created:
                print "RE",ce_obj,pos,city
                

        fd.close()

