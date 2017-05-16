#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import RepositoryCacheAuthor

class Command(BaseCommand):
    args = ''
    help = 'Clean repository cache author'

    def handle(self, *args, **options):
        types=args

        for aut in RepositoryCacheAuthor.objects.all():
            if "," in str(aut.name):
                t=[x.strip() for x in str(aut.name).split(",")]
                t.reverse()
                aut.name=" ".join(t)
            if ( ( "aa" in str(aut.name) 
                   or "AA" in str(aut.name) )
                 and ( "vv" in str(aut.name) 
                   or "VV" in str(aut.name) ) ):
                aut.name="AA. VV."
                aut.save()
                return
            t=list(filter(bool,aut.name.split(" ")))
            for n in range(0,len(t)):
                if len(t[n])==1: t[n]+="."
            aut.name=" ".join(t)
            aut.save()
            
