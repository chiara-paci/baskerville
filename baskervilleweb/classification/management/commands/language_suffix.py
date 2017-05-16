#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


from classification.models import Argument,ArgumentSuffixCollection,ArgumentSuffix

class Command(BaseCommand):
    args = ''
    help = 'Rebuild argument identifier'

    def handle(self, *args, **options):
        lang61=list(Argument.objects.filter(identifier__istartswith="6.1"))
        lang62=list(Argument.objects.filter(identifier__istartswith="6.2"))
        nolang_ids=[x.id for x in lang61+lang62]
        objs=Argument.objects.filter(identifier__istartswith="6.").exclude(id__in=nolang_ids)
        coll=ArgumentSuffixCollection.objects.get(name="language")
        obj_dict={}
        base=Argument.objects.get(identifier="6")
        suffix_zero=ArgumentSuffix.objects.get(id=0)
        for obj in objs:
            if obj.parent.id==base.id:
                suffix,created=ArgumentSuffix.objects.get_or_create(collection=coll,name=obj.name,number=obj.number,parent=suffix_zero)
            else:
                parent=obj_dict[obj.parent.id]
                suffix,created=ArgumentSuffix.objects.get_or_create(collection=coll,name=obj.name,number=obj.number,parent=parent)
            obj_dict[obj.id]=suffix
            if created:
                print("created:",suffix)
