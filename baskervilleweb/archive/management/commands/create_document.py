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

from .utility import store_asset

def add_src(doc,src_base,src,dirasset,dirthumb):
    src_path=os.path.join(src_base,src)
    if not os.path.isfile(src_path):
        os.makedirs(os.path.join(dirasset,src),exist_ok=True)
        os.makedirs(os.path.join(dirthumb,src),exist_ok=True)
        for fname in os.listdir(src_path):
            if fname.startswith("."): continue
            add_src(doc,src_base,os.path.join(src,fname),dirasset,dirthumb)
        return

    print(src_path)
    asset_path=os.path.join(dirasset,src)
    thumb_path=os.path.join(dirthumb,src+".jpeg")
    print("    ",asset_path)
    print("    ",thumb_path)
    shutil.copy2(src_path,asset_path)
    asset=store_asset(doc,asset_path,thumb_path)

class Command(BaseCommand):
    help = 'Used to import a photo.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('collection')
        parser.add_argument('name')
        parser.add_argument('src_list',nargs='+')

    def handle(self, *args, **options):
        src_list=[ os.path.abspath(p) for p in options["src_list"] ]
        name=options["name"]
        collection=options["collection"]

        src_base=os.path.commonpath(src_list)
        src_list=[ os.path.relpath(p,start=src_base) for p in src_list ]

        dirasset=os.path.join(settings.ARCHIVE_PATH["document_asset"]["full"],
                              collection,name)
        dirthumb=os.path.join(settings.ARCHIVE_PATH["document_asset"]["thumb"],
                              collection,name)
        os.makedirs(dirasset,exist_ok=True)
        os.makedirs(dirthumb,exist_ok=True)

        coll,created=models.DocumentCollection.objects.get_or_create(name=collection)
        doc,created=models.Document.objects.get_or_create(name=name)
        coll.documents.add(doc)

        for src in src_list:
            add_src(doc,src_base,src,dirasset,dirthumb)
            # src_path=os.path.join(src_base,src)
            # print(src_path)
            # if os.path.isfile(src_path):
            #     asset_path=os.path.join(dirasset,src)
            #     thumb_path=os.path.join(dirthumb,src+".jpeg")
            #     print("    ",asset_path)
            #     print("    ",thumb_path)
            #     #shutil.copy2(src,asset_path)
            #     #asset=store_asset(doc,asset_path,thumb_path)
            #     continue
            # for fname in os.listdir(src_path):
            #     if fname.startswith("."): continue
            #     full_path=os.path.join(src_path,fname)
            #     if not os.path.isfile(full_path): continue
            #     asset_path=os.path.join(dirasset,src,fname)
            #     thumb_path=os.path.join(dirthumb,src,fname+".jpeg")
            #     print("    ",full_path)
            #     print("        ",asset_path)
            #     print("        ",thumb_path)



        #     photo=store_photo(photo_path,thumb_path)
        #     if not photo: 
        #         print(full_path,"failed")                                                                                                                                                                          
        #         continue
        #     store_exif_data(photo)
        #     print(full_path,"ok")



        # for fname in os.listdir(src_dir):
        #     if fname.startswith("."): continue
        #     fname,ext=os.path.splitext(fname)

        #     full_path=os.path.join(src_dir,fname+ext)
        #     if not os.path.isfile(full_path): continue
        #     photo_path=os.path.join(dirasset,fname+ext)
        #     thumb_path=os.path.join(dirthumb,fname+".jpeg")
        #     shutil.copy2(full_path,photo_path)
        #     photo=store_photo(photo_path,thumb_path)
        #     if not photo: 
        #         print(full_path,"failed")
        #         continue
        #     store_exif_data(photo)
        #     print(full_path,"ok")

        # # shutil.copy2(src,dst)

        # # dirasset=os.path.dirname(photo_path)
        # # fname=os.path.basename(photo_path)
        # # fname,ext=os.path.splitext(fname)

        # # reldir=os.path.relpath(dirasset,models.PHOTO_ARCHIVE_FULL)

        # # thumb_path=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir,fname+".jpeg")
        # # os.makedirs(os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir),exist_ok=True)

        # # photo=store_photo(photo_path,thumb_path)
        # # store_exif_data(photo)

