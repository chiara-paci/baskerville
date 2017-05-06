#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import ProductMicroNutrient,MicroNutrient,MicroNutrientClass

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    # 1 sale : .4 sodio = S sale : N sodio
    # S=N*1/.4=N/.4=10*N/4
    # N=.4*S

    def handle(self, *args, **options):
        sali_minerali,created=MicroNutrientClass.objects.get_or_create(name="sali minerali")
        sale,created=MicroNutrient.objects.get_or_create(name="sale",defaults={"nutrient_class": sali_minerali})
        sodio,created=MicroNutrient.objects.get_or_create(name="sodio",defaults={"nutrient_class": sali_minerali})

        for micro in ProductMicroNutrient.objects.filter(micro_nutrient__in=[sale,sodio]):
            sale_sodio=micro.product.productmicronutrient_set.filter(micro_nutrient__in=[sale,sodio])
            if len(sale_sodio)==1:
                obj_a=sale_sodio[0]
                if obj_a.micro_nutrient==sale:
                    obj_b=ProductMicroNutrient.objects.create(product=obj_a.product,micro_nutrient=sodio,
                                                              quantity=.4*obj_a.quantity)
                    
                if obj_a.micro_nutrient==sodio:
                    obj_b=ProductMicroNutrient.objects.create(product=obj_a.product,micro_nutrient=sale,
                                                              quantity=obj_a.quantity/.4)
            else:
                obj_a,obj_b=sale_sodio[:2]
            if obj_a.micro_nutrient==sale:
                obj_sale=obj_a
                obj_sodio=obj_b
            else:
                obj_sale=obj_b
                obj_sodio=obj_a
            if obj_sodio.quantity != .4*obj_sale.quantity:
                print("ERR",micro.product,"sodio =",obj_sodio.quantity,"sale =",obj_sale.quantity,"sodio exp. =",.4*obj_sale.quantity)
