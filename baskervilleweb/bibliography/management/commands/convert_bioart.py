#! /usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Category,CategoryRelation,CategoryPlaceRelation,Place

map_categories= {
    "austriache": 15,
    "belghe": 30,
    "ceche": 31,
    "fiamminghe": 32,
    "francesi": 22,
    "greche": 33,
    "inglesi": 9,
    "irlandesi": 34,
    "italiane": 16,
    "messicane": 35,
    "norvegesi": 36,
    "olandesi": 37,
    "russe": 38,
    "spagnole": 39,
    "statunitensi": 40,
    "svizzere": 41,
    "tedesche": 1 }

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        bio_art=Category.objects.get(name="biografie artistiche")

        for cat_label in list(map_categories.keys()):
            cat_name="biografie artistiche "+cat_label
            print(cat_name)
            place=Place.objects.get(id=map_categories[cat_label])
            for cat_rel in CategoryRelation.objects.filter(father__name=cat_name):
                child=cat_rel.child
                obj,created=CategoryPlaceRelation.objects.get_or_create(category=child,place=place)
                cat_rel.father=bio_art
                cat_rel.save()
                print("    ",child)
