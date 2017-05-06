#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Book,PublisherIsbn

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
            if len(t)!=5: 
                print(t)
                continue

            isbn_ced=t[0].strip()
            isbn_book=t[1].strip()
            isbn_crc=t[2].strip()
            title=t[3].strip()
            year=t[4].strip()

            try:
                pub_isbn_obj=PublisherIsbn.objects.get(isbn=isbn_ced)
            except ObjectDoesNotExist as e:
                print("NE isbn_ced:",isbn_ced)
                sys.exit()
            pub_isbn_obj.update_preferred()
            pub_obj=pub_isbn_obj.preferred

            book,created=Book.objects.get_or_create(isbn_ced=isbn_ced,isbn_book=isbn_book,
                                                    defaults={"title":title,"year":year,"publisher":pub_obj})

            if created:
                print("Created: ",book)

            book.update_crc()
            if str(book.isbn_crc10)!=isbn_crc:
                print("Verifica: ",book.isbn10(),isbn_ced,isbn_book,isbn_crc,book)


        fd.close()

