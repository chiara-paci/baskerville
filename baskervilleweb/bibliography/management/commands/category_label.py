#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import CategoryTreeNode

class Command(BaseCommand):
    args = 'types'
    help = 'Update cache\ntypes: author_names, issn_crc, preferred_publisher, publication_years'

    def handle(self, *args, **options):
        cat_list=CategoryTreeNode.objects.all()
        L=len(cat_list)
        next_perc=10
        n=0
        for cat in cat_list:
            cat.save()
            n+=1
            if 100.0*float(n)/float(L) > next_perc:
                print("    %2.2f%%" % (100*float(n)/float(L)))
                next_perc+=10
