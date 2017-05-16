"""
Management utility to create superusers.
"""

from django.conf import settings

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError

from PIL import Image
from archive import models

import os.path,os

class Command(BaseCommand):
    help = 'Used to import a photo.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('photo')

    def handle(self, *args, **options):
        photo=options["photo"]

        dirphoto=os.path.dirname(photo)
        fname=os.path.basename(photo)

        fname,ext=os.path.splitext(fname)

        print(photo)

        reldir=os.path.relpath(dirphoto,models.PHOTO_ARCHIVE_FULL)

        thumb_fname=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir,fname+".jpeg")

        os.makedirs(os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir),exist_ok=True)

        print(thumb_fname)
        try:
            im = Image.open(photo)
            im.thumbnail( (128,128) )
            im.save(thumb_fname, "JPEG")
            im.close()
        except IOError:
            print("cannot create thumbnail for", photo)

        im = Image.open(photo)
        
        print(dir(im))
        print(im.format,im.format_description,im.size,im.width,im.height,im.info,im.mode)
        

