#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import RepositoryCacheBook,Book

class Command(BaseCommand):
    args = ''
    help = 'Clean repository cache book'

    def handle(self, *args, **options):
        types=args

        for rbook in RepositoryCacheBook.objects.all():
            isbn=rbook.isbn
            rbook.year=rbook.year.strip()
            if len(isbn)==13:
                objs=Book.objects.filter(isbn_cache13=isbn)
                if objs:
                    rbook.indb=True
            else:
                objs=Book.objects.filter(isbn_cache10=isbn)
                if objs:
                    rbook.indb=True
            rbook.save()
                
                
            
