#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import ProductMicroNutrient

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        for micro in ProductMicroNutrient.objects.all():
            micro.quantity=1000*micro.quantity
            micro.save()
