#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Article,Issue

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
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

            issn_pub=t[1].strip()
            issn_num=t[2].strip()
            title=t[3].strip()
            pages=t[4].strip()
            t=pages.split("-")
            page_begin=t[0]
            page_end=t[1]

            try:
                issue=Issue.objects.get(volume__pubblication__issn=issn_pub,issn_num=issn_num)
            except ObjectDoesNotExist, e:
                print "NE issue:",issn_pub,issn_num
                sys.exit()

            article,created=Article.objects.get_or_create(issue=issue,page_begin=page_begin,page_end=page_end,
                                                          defaults={"title":title})

            if created:
                print "Created: ",article



        fd.close()

