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

from .utility import store_exif_data,store_photo


class Command(BaseCommand):
    help = 'Reset thumbnail of all photos.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        for photo in models.Photo.objects.all():
            dirphoto=os.path.dirname(photo.full_path)
            fname=os.path.basename(photo.full_path)
            fname,ext=os.path.splitext(fname)
            reldir=os.path.relpath(dirphoto,models.PHOTO_ARCHIVE_FULL)
            dirthumb=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir)
            os.makedirs(dirthumb,exist_ok=True)
            thumb_path=os.path.join(dirthumb,fname+".jpeg")
            try:
                im = Image.open(photo.full_path)
                im.thumbnail( (128,128) )
                im.save(thumb_path, "JPEG")
                im.close()
            except IOError:
                print("cannot create thumbnail for", photo_path)
                continue
            photo.thumb_path=thumb_path
            photo.save()
            print(thumb_path)
