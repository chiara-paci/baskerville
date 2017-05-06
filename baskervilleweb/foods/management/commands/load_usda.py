#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import UsdaNndFoodGroup,UsdaNndFood

import urllib.request, urllib.error, urllib.parse
import re

def null_or_float(val):
    if not val: return 0
    return float(val)

def load_food_group(t):
    usda_id=t[0].replace('~','')
    name=t[1].replace('~','')
    food_group,created=UsdaNndFoodGroup.objects.get_or_create(name=name,usda_id=usda_id)
    if created:
        print("FGRP",food_group)

def load_food(t):
    usda_id=t[0].replace('~','')
    food_group_usda_id=t[1].replace('~','')
    food_group = UsdaNndFoodGroup.objects.get(usda_id=food_group_usda_id)
    long_description = t[2].replace('~','')
    short_description = t[3].replace('~','')
    common_name = t[4].replace('~','')
    manufacturer_name = t[5].replace('~','')
    survey = bool(t[6].replace('~',''))
    refuse_desc = t[7].replace('~','')
    refuse_perc = null_or_float(t[8])
    scientific_name = t[9].replace('~','')
    nitrogen_factor = null_or_float(t[10])
    protein_factor = null_or_float(t[11])
    fat_factor = null_or_float(t[12])
    carbohydrate_factor = null_or_float(t[13])

    food,created=UsdaNndFood.objects.get_or_create(usda_id=usda_id,
                                                   defaults={ "food_group": food_group,
                                                              "long_description": long_description,
                                                              "short_description": short_description,
                                                              "common_name": common_name,
                                                              "manufacturer_name": manufacturer_name,
                                                              "survey": survey,
                                                              "refuse_desc": refuse_desc,
                                                              "refuse_perc": refuse_perc,
                                                              "scientific_name": scientific_name,
                                                              "nitrogen_factor": nitrogen_factor,
                                                              "protein_factor": protein_factor,
                                                              "fat_factor": fat_factor,
                                                              "carbohydrate_factor": carbohydrate_factor })
    if created:
        print("FOOD",food)
        return
    food.food_group=food_group
    food.long_description=long_description
    food.short_description=short_description
    food.common_name=common_name
    food.manufacturer_name=manufacturer_name
    food.survey=survey
    food.refuse_desc=refuse_desc
    food.refuse_perc=refuse_perc
    food.scientific_name=scientific_name
    food.nitrogen_factor=nitrogen_factor
    food.protein_factor=protein_factor
    food.fat_factor=fat_factor
    food.carbohydrate_factor=carbohydrate_factor
    food.save()

MAP_FILES= [
    ( "FD_GROUP.txt", load_food_group ),
    ( "FOOD_DES.txt", load_food )
    ]


class Command(BaseCommand):
    args = '<fdir>'
    help = 'Load USDA National Nutrient Database'

    def handle(self, *args, **options):
        fdir = args[0]
        if fdir[-1]=='/': fdir=fdir[:-1]
        for fname,load_func in MAP_FILES:
            fd=open(fdir+"/"+fname,'r')
            for r in fd.readlines():
                t=r.strip().split('^')
                load_func(t)
            fd.close()
