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

class Command(BaseCommand):
    help = 'Migrate to asset.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        for photo in models.Photo.objects.all():
            relname=os.path.relpath(photo.full_path,
                                    settings.ARCHIVE_PATH["photo"]["full"])
            photo_d,created=models.PhotoD.objects.get_or_create(label=relname,defaults={"description": photo.description})
            photo.photo=photo_d
            photo.save()
            print(photo_d.label)
