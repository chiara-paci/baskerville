#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from classification.models import Argument,ArgumentSuffixCollection,ArgumentClassification

class Command(BaseCommand):
    args = ''
    help = 'Rebuild argument classification'

    def handle(self, *args, **options):
        for argclass in ArgumentClassification.objects.all():
            if argclass.classification_set.exists(): continue
            if argclass.shortclassification_set.exists(): continue
            print "Delete",argclass
            argclass.delete()
        for arg in Argument.objects.all():
            if arg.id==0: continue
            argclass,created=ArgumentClassification.objects.get_or_create(number=arg.identifier,
                                                                          defaults={"name": arg.name })
            if created:
                print "Created",argclass
        for suffixcollection in ArgumentSuffixCollection.objects.all():
            for arg in suffixcollection.roots():
                if arg.id==0: continue
                for suffix in suffixcollection.argumentsuffix_set.all():
                    if suffix.id==0: continue
                    number=arg.identifier+suffix.identifier
                    name=arg.name+". "+suffix.name
                    argclass,created=ArgumentClassification.objects.get_or_create(number=number,
                                                                                  defaults={"name": name })
                    if created:
                        print "Created",argclass
                    
