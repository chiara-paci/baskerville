#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from classification.models import Argument,ArgumentSuffix

class Command(BaseCommand):
    args = ''
    help = 'Rebuild argument identifier'

    def handle(self, *args, **options):

        for arg in Argument.objects.all():
            arg.save()
        for arg in ArgumentSuffix.objects.all():
            arg.save()


