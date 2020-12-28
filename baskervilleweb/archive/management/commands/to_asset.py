"""
Management utility to create superusers.
"""

from django.conf import settings

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError

from PIL import Image
from PIL.ExifTags import TAGS,GPSTAGS
from archive import models

import os.path,os
import magic
import exifread
import dateutil.parser
# import libxmp.utils
import datetime,pytz
import shutil

def myslug(x):
    x,ext=os.path.splitext(x)
    x=x.replace("/",".")
    x=x.replace("%",".")
    return x

class Command(BaseCommand):
    help = 'Migrate to asset.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        for photo in models.Photo.objects.all():
            photo.photo.cover=photo
            photo.photo.save()
            print(photo.photo.label)
