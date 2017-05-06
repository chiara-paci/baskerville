#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django.utils.timezone import make_aware

import datetime

from foods.models import Recipe,RecipeProduct,MeasureUnit,Product

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
        print("Measure %s not available" % measure_name)
        return None
    if len(measure_list) > 1:
        print("Too many measures:")
        for m in measure_list:
            print("    ",m)
        return None
    return measure_list.first()

def search_product(product_name):
    product_list=Product.objects.filter(name__iexact=product_name)
    if not product_list:
        product_list=Product.objects.filter(name__icontains=product_name)
    if not product_list:
        print("Product %s not available" % product_name)
        return None
    if len(product_list) > 1:
        print("Too many products:")
        for m in product_list:
            print("    ",m)
        return None
    return product_list.first()

class Command(BaseCommand):
    args = 'name frecipe [ [day] time ]'
    help = 'Add chiara\'s diary entry based on recipe'

    def handle(self, *args, **options):
        name=args[0]
        recipe_file = args[1]
        d_time=convert_date_time(args[2:])

        fd=open(recipe_file,'r')
        ingredients={}
        finale={}
        for r in fd.readlines():
            r=r.strip()
            if not r: continue
            t=r.split(":")
            if t[0]=="finale":
                finale={"measure":t[2],"quantity":float(t[1])}
                continue
            ingredients[t[1]]={"measure":t[3],"quantity":float(t[2])}
        fd.close()

        if not finale:
            recipe,create=Recipe.objects.get_or_create(name=name,time=d_time)
        else:
            measure=search_measure(finale["measure"])
            if not measure: return
            totale_finale=measure.factor*finale["quantity"]
            recipe,created=Recipe.objects.get_or_create(name=name,time=d_time,defaults={"final_weight":totale_finale})
            if not created:
                recipe.final_weight=totale_finale
                recipe.save()

        errors=False
        for product_name in list(ingredients.keys()):
            measure=search_measure(ingredients[product_name]["measure"])
            product=search_product(product_name)
            if not measure: 
                errors=True
                continue
            if not product: 
                errors=True
                continue
            ingredients[product_name]["product"]=product

        if errors: return
        
        for product_name in list(ingredients.keys()):
            prod,created=RecipeProduct.objects.get_or_create(recipe=recipe,
                                                             product=ingredients[product_name]["product"],
                                                             defaults={"quantity":ingredients[product_name]["quantity"],
                                                                       "measure_unit":measure})
            if not created:
                prod.quantity=ingredients[product_name]["quantity"]
                prod.measure_unit=measure
                prod.save()

        recipe.save()

