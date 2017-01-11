#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from foods.models import FoodDiaryEntry

class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        for obj in FoodDiaryEntry.objects.all():
            obj.save()
