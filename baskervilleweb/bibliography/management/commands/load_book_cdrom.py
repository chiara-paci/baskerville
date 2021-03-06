#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Book,TextsCdrom

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
            if len(t)!=4: 
                print(t)
                continue

            isbn_ced=t[0].strip()
            isbn_book=t[1].strip()
            cdrom_ced=t[2].strip().lower()
            cdrom_ind=t[3].strip().lower()
            cdrom_label=cdrom_ced+cdrom_ind

            try:
                cd_obj=TextsCdrom.objects.get(label=cdrom_label)
            except ObjectDoesNotExist as e:
                print("NE cd:",cdrom_label)
                sys.exit()

            try:
                book_obj=Book.objects.get(isbn_ced=isbn_ced,isbn_book=isbn_book)
            except ObjectDoesNotExist as e:
                print("NE book:",isbn_ced,isbn_book)
                sys.exit()
                
            print("CD",cd_obj,": ADD",book_obj)
            cd_obj.books.add(book_obj)
                

        fd.close()

