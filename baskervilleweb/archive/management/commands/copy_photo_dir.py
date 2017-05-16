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
import shutil

from .utility import store_exif_data,store_photo


class Command(BaseCommand):
    help = 'Used to import a photo.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('src_dir')
        parser.add_argument('dest_rel_dir')

    def handle(self, *args, **options):
        src_dir=options["src_dir"]
        reldir=options["dest_rel_dir"]

        dirphoto=os.path.join(models.PHOTO_ARCHIVE_FULL,reldir)
        dirthumb=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir)

        os.makedirs(dirphoto,exist_ok=True)
        os.makedirs(dirthumb,exist_ok=True)

        for fname in os.listdir(src_dir):
            if fname.startswith("."): continue
            fname,ext=os.path.splitext(fname)

            full_path=os.path.join(src_dir,fname+ext)
            if not os.path.isfile(full_path): continue
            photo_path=os.path.join(dirphoto,fname+ext)
            thumb_path=os.path.join(dirphoto,fname+".jpeg")
            shutil.copy2(full_path,photo_path)
            photo=store_photo(photo_path,thumb_path)
            if not photo: 
                print(full_path,"failed")
            store_exif_data(photo)
            print(full_path,"ok")

        # shutil.copy2(src,dst)

        # dirphoto=os.path.dirname(photo_path)
        # fname=os.path.basename(photo_path)
        # fname,ext=os.path.splitext(fname)

        # reldir=os.path.relpath(dirphoto,models.PHOTO_ARCHIVE_FULL)

        # thumb_path=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir,fname+".jpeg")
        # os.makedirs(os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir),exist_ok=True)

        # photo=store_photo(photo_path,thumb_path)
        # store_exif_data(photo)

