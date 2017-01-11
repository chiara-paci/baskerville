#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django.utils.timezone import make_aware

import datetime

from foods.models import FoodDiaryEntry,MeasureUnit,Product,Recipe,RecipeProduct

def convert_date_time(params):
    def parse_time(time_str):
        if time_str[0]=="b":
            return 7,15,0
        if time_str[0]=="l":
            return 12,30,0
        if time_str[0]=="d":
            return 19,30,00
        t=time_str.split(":")
        if len(t)==1:
            return int(t[0]),0,0
        if len(t)==2:
            return int(t[0]),int(t[1]),0
        return int(t[0]),int(t[1]),int(t[2])
    
    def parse_date(date_str):
        today=datetime.datetime.today()
        if date_str[0]=="t":
            return today.year,today.month,today.day
        yesterday=today-datetime.timedelta(days=1)
        if date_str[0]=="y":
            return yesterday.year,yesterday.month,yesterday.day
        t=date_str.split("-")
        return int(t[0]),int(t[1]),int(t[2])

    if not params or params[0][0]=="n":
        return make_aware(datetime.datetime.today())
    if len(params)==1:
        hour,minute,second=parse_time(params[0])
        year,month,day=parse_date("t")
    else:
        hour,minute,second=parse_time(params[1])
        year,month,day=parse_date(params[0])
    return make_aware(datetime.datetime(year,month,day,hour,minute,second))

### 640 g

def search_measure(measure_name):
    measure_list=MeasureUnit.objects.filter(name__iexact=measure_name)
    if not measure_list:
        measure_list=MeasureUnit.objects.filter(name__icontains=measure_name)
    if not measure_list:
        print "Measure %s not available" % measure_name
        return None
    if len(measure_list) > 1:
        print "Too many measures:"
        for m in measure_list:
            print "    ",m
        return None
    return measure_list.first()

def search_product(product_name):
    product_list=Product.objects.filter(name__iexact=product_name)
    if not product_list:
        product_list=Product.objects.filter(name__icontains=product_name)
    if not product_list:
        print "Product %s not available" % product_name
        return None
    if len(product_list) > 1:
        print "Too many products:"
        for m in product_list:
            print "    ",m
        return None
    return product_list.first()

def search_recipe(recipe_name,recipe_date):
    recipe_list=Recipe.objects.filter(name__iexact=recipe_name)
    if not recipe_list:
        recipe_list=Recipe.objects.filter(name__icontains=recipe_name)
    if not recipe_list:
        print "Recipe %s not available" % recipe_name
        return None
    if len(recipe_list) > 1:
        recipe_list=recipe_list.filter(time__year=recipe_date.year,
                                       time__month=recipe_date.month,
                                       time__day=recipe_date.day)
    if len(recipe_list) > 1:
        print "Too many recipes:"
        for m in recipe_list:
            print "    ",m,m.time
        return None
    return recipe_list.first()

class Command(BaseCommand):
    args = 'qta mis recipename recipedate [ [day] time ]'
    help = 'Add chiara\'s diary entry based on recipe'

    def handle(self, *args, **options):
        user = User.objects.get(username='chiara')
        quantity = float(args[0])
        measure_name = args[1]
        recipe_name = args[2]
        recipe_date = convert_date_time([ args[3],"00:00" ])
        d_time=convert_date_time(args[3:])

        measure=search_measure(measure_name)
        if not measure: return
        recipe=search_recipe(recipe_name,recipe_date)
        if not recipe: return

        quantity_real=measure.factor*quantity

        totale_iniziale=recipe.total_weight
        totale_finale=recipe.final_weight

        portion_factor=quantity_real/float(totale_finale)

        measure=MeasureUnit.objects.get(name="g")
        
        for rp in recipe.recipeproduct_set.all():
            quota=portion_factor*rp.quantity_real()
            print rp,quota,"g"
            FoodDiaryEntry.objects.create(user=user,time=d_time,product=rp.product,
                                          quantity=quota,measure_unit=measure)

        # product_list=Product.objects.filter(name__iexact=product_name)
        # if not product_list:
        #     product_list=Product.objects.filter(name__icontains=product_name)
        # if not product_list:
        #     print "Product %s not available" % product_name
        #     return
        # if len(product_list) > 1:
        #     print "Too many products:"
        #     for m in product_list:
        #         print "    ",m
        #     return
        # product=product_list.first()

    

        #print d_time,product,quantity,measure
        #
