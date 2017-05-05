#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import UsdaNndFoodGroup

import urllib2
import re

class Command(BaseCommand):
    args = '<fname>'
    help = 'Load food group description from USDA National Nutrient Database'

    def handle(self, *args, **options):
        fname = args[0]
        fd=open(fname,'r')
        for r in fd.readlines():
            t=r.strip().split('^')
            usda_id=t[0].replace('~','')
            name=t[1].replace('~','')
            food_group,created=UsdaNndFoodGroup.objects.get_or_create(name=name,usda_id=usda_id)
            print food_group,created

