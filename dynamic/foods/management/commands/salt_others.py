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
        sodio=MicroNutrient.objects.get(name="sodio")
        potassio=MicroNutrient.objects.get(name="potassio")
        fibre=MicroNutrient.objects.get(name="fibre")
        acqua=MicroNutrient.objects.get(name="acqua")

        for rel in sodio.productmicronutrient_set.all():
            print rel.product
            rel.product.sodium=rel.quantity/1000.0
            rel.product.save()

        for rel in potassio.productmicronutrient_set.all():
            rel.product.potassium=rel.quantity/1000.0
            rel.product.save()

        for rel in fibre.productmicronutrient_set.all():
            rel.product.fiber=rel.quantity/1000.0
            rel.product.save()

        for rel in acqua.productmicronutrient_set.all():
            rel.product.water=rel.quantity/1000.0
            rel.product.save()
