#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import ProductMicroNutrient,Product,Vendor,MicroNutrient,ProductCategory

import urllib2
import re

class Command(BaseCommand):
    args = '<nome> <cat> <url>'
    help = 'Carica alimento da DietaBit'

    def handle(self, *args, **options):
        prod_name=args[0]
        cat_name=args[1]
        url=args[2]

        response = urllib2.urlopen(url)
        status="header"
        tables=[]
        current=[]
        for r in response.readlines():
            r=r.strip()
            if not r: continue
            if r[:6]=='<table' or r[:25]=='<tr class="gruppoValori">':
                if current:
                    tables.append(current)
                    current=[]
                current.append(r)
                status="read"
                continue
            if status!="read": continue
            
            current.append(r)
        if current:
            tables.append(current)
        vals=[]
        salva=True
        for tab in tables:
            for r in tab:
                r=re.sub(r'^<tr.*?><td.*?>','',r)
                r=re.sub('</td><td.*?>',':',r)
                r=re.sub(r'</?a.*?>','',r)
                if r[0]=='<': continue
                r=re.sub(r'<.*?>','',r)
                r=r.strip()
                if not r: continue
                t=r.split(":")
                if len(t)==1: 
                    salva=(r in ["Nutrienti principali","Minerali","Vitamine" ])
                    continue
                if not salva: continue
                if len(t)>=2:
                    t[1]=t[1].replace(",",".")
                    try:
                        t[1]=float(t[1])
                    except ValueError, e:
                        continue
                    vals.append( (t[0].lower(),t[1],t[2]) )

        base={
            "proteine": (0,"g"),
            "carboidrati": (0,"g"),
            "zuccheri": (0,"g"),
            "grassi": (0,"g"),
            "saturi": (0,"g"),
            "calorie": (0,"g"),
            "sodio": (0,"g"),
            "potassio": (0,"g"),
            "fibre": (0,"g"),
            "acqua": (0,"g"),
            }
        escludi = [ "valore energetico (calorie)",
                    "luteina + zeaxantina",
                    "diidrofillochinone",
                    "monoinsaturi",
                    "acido folico",
                    "folati alimentari",
                    "folati (dfe)",
                    "vitamina b12 (aggiunta)",
                    "vitamina e (aggiunta)",
                    "beta-tocoferolo",
                    "gamma-tocoferolo",
                    "delta-tocoferolo",
                    "retinolo","vitamina d (d2+d3)",
                    "beta-carotene",
                    "alfa-carotene",
                    "criptoxantina",
                    "vitamina a, iu",
                    "licopene",
                    "polinsaturi","ceneri","fibra alimentare" ]

        vit_map={
            "vitamina a (rae)":                "A (retinolo)",
            "tiamina (vitamina b1)":           "B1 (tiamina)",
            "riboflavina (vitamina b2)":       "B2 (riboflavina)",
            "niacina (vitamina b3 o pp)":      "B3 (PP - niacina)",
            "acido pantotenico (vitamina b5)": "B5 (W - acido pantotenico)",
            "piridossina (vitamina b6)":       "B6 (Y - piridossina)",
            "folati":                          "B9 (M - acido folico - folacina)",
            "vitamina b12":                    "B12 (cobalamina)",
            "vitamina c (acido ascorbico)":    "C (acido ascorbico)",
            "vitamina d":                      "D",
            "vitamina e":                      "E (tocoferolo)",
            "vitamina k":                      "K",
            "colina":                          "J (colina)",
            }

        micro=[]

        for t in vals:
            if t[0] in base.keys():
                base[t[0]]=(t[1],t[2])
                continue
            if t[0] in escludi: continue
            if t[0] in vit_map.keys():
                micro.append( (vit_map[t[0]],t[1],t[2]) )
            else:
                micro.append(t)

        print base

        for name,(val,mis) in base.items():
            print "B %40.40s %10.2f %s" % (name,val,mis)

        for name in base.keys():
            if base[name][1]=="mg":
                base[name]=(base[name][0]/1000.0,"g")
            
        vendor,created=Vendor.objects.get_or_create(name="generico")
        category,created=ProductCategory.objects.get_or_create(name=cat_name)

        print vendor,category

        product,created=Product.objects.get_or_create(name=prod_name.lower(),
                                                      defaults={ "category": category,
                                                                 "vendor": vendor,
                                                                 "kcal": base["calorie"][0],
                                                                 "fat": base["grassi"][0],
                                                                 "saturated_fat": base["saturi"][0],
                                                                 "carbohydrate": base["carboidrati"][0],
                                                                 "sugar": base["zuccheri"][0],
                                                                 "sodium": base["sodio"][0],
                                                                 "potassium": base["potassio"][0],
                                                                 "fiber": base["fibre"][0],
                                                                 "water": base["acqua"][0],
                                                                 "protein": base["proteine"][0] })
        product.category=category
        product.vendor=vendor
        product.kcal=base["calorie"][0]
        product.fat=base["grassi"][0]
        product.saturated_fat=base["saturi"][0]
        product.carbohydrate=base["carboidrati"][0]
        product.sugar=base["zuccheri"][0]
        product.sodium=base["sodio"][0]
        product.potassium=base["potassio"][0]
        product.fiber=base["fibre"][0]
        product.water=base["acqua"][0]
        product.protein=base["proteine"][0]
        product.save()

        print product

        for name,val,mis in micro:
            if not val: continue
            try:
                micro_obj=MicroNutrient.objects.get(name=name)
            except MicroNutrient.DoesNotExist, e:
                print "micro nutrient %s non esiste" % name
                continue
            if mis=="g": V=val*1000
            elif mis!="mg": V=val/1000.0
            else:V=val
            print "  %40.40s %10.6f mg %10.6f %s" % (micro_obj,V,val,mis)
            prod_mnut,created=ProductMicroNutrient.objects.get_or_create(product=product,
                                                                         micro_nutrient=micro_obj,
                                                                         defaults={ "quantity": V })
            #print "  %40.40s %10.2f %s" % (unicode(micro_obj),val,mis)
        

