#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import PublisherState,PublisherAddress

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load authors'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=str(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=[x.strip() for x in l.split(":")]
            city=t[0]
            state=t[1]
            state_obj,created=PublisherState.objects.get_or_create(name=state)
            if created:
                print("CS",state_obj)
            city_obj,created=PublisherAddress.objects.get_or_create(city=city,state=state_obj)
            if created:
                print("CC",city_obj)
        fd.close()

