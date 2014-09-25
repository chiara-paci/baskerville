#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

import bibliography.booksearch as booksearch

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Search by isbn'

    def handle(self, *args, **options):
        elenco=args[0]
        isbn_list=[]
        fd=open(elenco,"r")
        for r in fd.readlines():
            r=r.strip()
            if not r: continue
            t=r.split(" ")
            isbn_list+=t
        fd.close()
        params=booksearch.look_for(isbn_list)

        print "Unseparable:"
        for isbn in params["unseparable"]:
            print "    ",isbn
            
        print "Not inserted:"
        L=[]
        for book in params["book_list"]:
            if book.indb: continue
            L.append(book.isbn_10())
        L.sort()
        n=0
        for isbn in L:
            print "    ",isbn
            if n<10:
                n+=1
                continue
            print
            n=0
