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
import libxmp.utils
import datetime,pytz

from .utility import store_exif_data,store_photo

class Command(BaseCommand):
    help = 'Used to import a photo.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('photo')

    def handle(self, *args, **options):
        photo_path=options["photo"]

        dirphoto=os.path.dirname(photo_path)
        fname=os.path.basename(photo_path)
        fname,ext=os.path.splitext(fname)

        reldir=os.path.relpath(dirphoto,models.PHOTO_ARCHIVE_FULL)

        thumb_path=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir,fname+".jpeg")
        os.makedirs(os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir),exist_ok=True)

        photo=store_photo(photo_path,thumb_path)
        store_exif_data(photo)

