#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Pubblication,Volume

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=str(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=[x.strip() for x in l.split("|")]
            if len(t)!=2: continue
            issn=t[0].strip()
            vol=t[1].strip()

            pub_obj=Pubblication.objects.get(issn=issn)
            vol_obj,created=Volume.objects.get_or_create(pubblication=pub_obj,label=vol)
            if created:
                print("Created: ",vol_obj)
                continue

        fd.close()

