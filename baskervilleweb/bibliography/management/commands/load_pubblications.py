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
    help = 'Load pubblications'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=map(lambda x: x.strip(),l.split("|"))
            issn=t[0]
            reg=t[1]
            title=t[2]
            vtype=t[3]
            try:
                reg_obj=MigrPublisherRiviste.objects.get(registro=reg)
            except ObjectDoesNotExist, e:
                print "NER",reg
                continue
            try:
                vtype_obj=VolumeType.objects.get(label=vtype)
            except ObjectDoesNotExist, e:
                print "NEV",vtype
                continue
            pub_obj,created=Pubblication.objects.get_or_create(issn=issn,title=title,publisher=reg_obj.publisher,volume_type=vtype_obj)
            if created:
                print "CPB",pub_obj
                

        fd.close()

