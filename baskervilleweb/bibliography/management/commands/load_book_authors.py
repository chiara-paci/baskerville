#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Book,MigrAuthor,BookAuthorRelation,AuthorRole

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
            if len(t)!=6: 
                print(t)
                continue

            isbn_ced=t[0].strip()
            isbn_book=t[1].strip()
            aut_cod=t[2].strip()
            aut_ind=t[3].strip()
            aut_role=t[4].strip()
            aut_pos=int(t[5].strip())

            if aut_cod=="A" and aut_ind=="0": continue

            try:
                migr_auth_obj=MigrAuthor.objects.get(cod=aut_cod,ind=aut_ind)
            except ObjectDoesNotExist as e:
                print("NE author:",aut_cod,aut_ind)
                sys.exit()
            
            author_obj=migr_auth_obj.author

            try:
                book_obj=Book.objects.get(isbn_ced=isbn_ced,isbn_book=isbn_book)
            except ObjectDoesNotExist as e:
                print("NE book:",isbn_ced,isbn_book)
                sys.exit()

            author_role,created=AuthorRole.objects.get_or_create(label=aut_role,
                                                                 defaults={"description":aut_role.capitalize()})


            if created:
                print("Created: ",author_role)

            author_book_rel,created=BookAuthorRelation.objects.get_or_create(author=author_obj,book=book_obj,
                                                                             author_role=author_role,
                                                                             defaults={"pos":aut_pos})
            if created:
                print("Created: ",author_book_rel)
                

        fd.close()

