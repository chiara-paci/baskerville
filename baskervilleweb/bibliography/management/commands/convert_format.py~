#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import Author,MigrAuthor,NameFormat,NameType,AuthorNameRelation

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load authors'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=map(lambda x: x.strip(),l.split("|"))
            obj={
                "cod": t[0],
                "ind": int(t[1]),
                "long": t[2],
                "short": t[3],
                "list": t[4],
                "ordering": t[5],
                "names": {}
                }
            for n in range(6,len(t)):
                q=t[n].split(":")
                obj["names"][q[0]]=q[1]
            lista.append(obj)

        fd.close()

        for obj in lista:
            long_format=NameFormat.objects.get(label=obj["long"])
            short_format=NameFormat.objects.get(label=obj["short"])
            list_format=NameFormat.objects.get(label=obj["list"])
            ordering_format=NameFormat.objects.get(label=obj["ordering"])

            author=Author.objects.create(long_format=long_format,
                                         short_format=short_format,
                                         list_format=list_format,
                                         ordering_format=ordering_format)
            ma=MigrAuthor.objects.create(author=author,cod=obj["cod"],ind=obj["ind"])
            for key,val in obj["names"].items():
                name_type=NameType.objects.get(label=key)
                anr=AuthorNameRelation.objects.create(author=author,name_type=name_type,value=val)
            author.save()
            print unicode(author)
