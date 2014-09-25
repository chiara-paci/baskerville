#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from classification.models import ArgumentSuffix,ArgumentSuffixCollection

class Command(BaseCommand):
    args = '<collection> <parent_identifier> <number> <name>'
    help = 'Add argument suffix'

    def handle(self, *args, **options):
        collection=args[0]
        parent_identifier=args[1]
        number=args[2]
        name=args[3]

        collection=ArgumentSuffixCollection.objects.get(name=collection)

        if parent_identifier:
            parent=ArgumentSuffix.objects.get(identifier=parent_identifier,collection=collection)
        else:
            parent=ArgumentSuffix.objects.get(id=0)

        arg_obj,created=ArgumentSuffix.objects.get_or_create(collection=collection,parent=parent,number=number,name=name)
        if created:
            print "Created:",arg_obj


