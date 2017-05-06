#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from classification.models import Argument

class Command(BaseCommand):
    args = '<parent_identifier> <number> <name>'
    help = 'Add argument'

    def handle(self, *args, **options):
        parent_identifier=args[0]
        number=args[1]
        name=args[2]

        parent=Argument.objects.get(identifier=parent_identifier)

        arg_obj,created=Argument.objects.get_or_create(parent=parent,number=number,name=name)
        if created:
            print("Created:",arg_obj)


