#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from bibliography.models import Author,NameFormat,NameFormatCollection

class Command(BaseCommand):
    help = 'Convert name formats'

    def handle(self, *args, **options):
        for author in Author.objects.all():
            test=(author.format_collection.long_format==author.long_format)            
            test=test and (author.format_collection.short_format==author.short_format)            
            test=test and (author.format_collection.list_format==author.list_format)            
            test=test and (author.format_collection.ordering_format==author.ordering_format)            
            if test: continue
            try:
                new_coll=NameFormatCollection.objects.get(long_format=author.long_format,
                                                          short_format=author.short_format,
                                                          list_format=author.list_format,
                                                          ordering_format=author.ordering_format)            
            except ObjectDoesNotExist as e:
                print(author)
                print("    ",author.long_format)
                print("    ",author.short_format)
                print("    ",author.list_format)
                print("    ",author.ordering_format)
                continue
            print(author)
            print("    ",author.format_collection,"=>",new_coll)
            author.format_collection=new_coll
            author.save()

                
            
