#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import Category,CategoryRelation

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
            child=t[0].strip()
            father=t[1].strip()

            child_obj,created=Category.objects.get_or_create(name=child)
            if father=="-":
                continue
            father_obj,created=Category.objects.get_or_create(name=father)

            rel,created=CategoryRelation.objects.get_or_create(father=father_obj,child=child_obj)
            if created:
                print(rel)
                

        fd.close()

