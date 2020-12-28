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
        for md in models.PhotoMetaDatum.objects.all():
            if md.label.name != "dpi": continue
            asset_md,created=models.PhotoAssetMetaDatum.objects.get_or_create(
                asset=md.photo.cover,
                label=md.label,
                value=md.value
            )
            print(md,asset_md)
            md.delete()
