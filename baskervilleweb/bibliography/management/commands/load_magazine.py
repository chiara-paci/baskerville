#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Pubblication,Volume,IssueType,Issue

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        comic_type=IssueType.objects.get(label="magazine")

        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=map(lambda x: x.strip(),l.split("|"))
            if len(t)!=5: 
                print t
                continue
            issn=t[0].strip()
            vol=t[1].strip()
            issn_num=t[2].strip()
            num=t[3].strip()
            day=t[4].strip()

            pub_obj=Pubblication.objects.get(issn=issn)
            vol_obj=Volume.objects.get(pubblication=pub_obj,label=vol)

            issue,created=Issue.objects.get_or_create(volume=vol_obj,issue_type=comic_type,issn_num=issn_num,
                                                      number=num,date=day)

            if created:
                print "Created: ",issue
                continue

        fd.close()

