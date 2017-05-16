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

def store_exif_data(photo):
    im=open(photo.full_path,"rb")

    tags=exifread.process_file(im,details=False)

    for tag in tags:
        t=tag.split()
        category=t[0]
        name=" ".join(t[1:])
        if not name: name="-"
        if type(tags[tag])==bytes:
            datatype,created=models.ExifType.objects.get_or_create(name="Bytes")
            tag_id=-1
            val=tags[tag]
        else:
            ftype=exifread.tags.FIELD_TYPES[tags[tag].field_type]
            datatype,created=models.ExifType.objects.get_or_create(name=ftype[2],short=ftype[1],exif_id=ftype[0])
            tag_id=tags[tag].tag
            val=str(tags[tag])
        label,created=models.ExifLabel.objects.get_or_create(name=name,category=category,
                                                             defaults={"type": datatype, "exif_id": tag_id})
        d,created=models.ExifDatum.objects.get_or_create(photo=photo,label=label,defaults={"value": val})
        if not created:
            d.value=val
            d.save()

        if label.name == "DateTime":
            dt=dateutil.parser.parse(val.replace(":","-",2)+" CET")
            photo.datetime=dt
            photo.save()

        if label.name == "Orientation":
            rotated="no"
            mirrored="no"
            t=val.split()
            if t[0]=="Mirrored":
                mirrored=t[1]
            if t[-1]=="180":
                rotated="180"
            if t[-1] in [ "CW","CCW" ]:
                rotated="90 "+t[-1].lower()
            photo.rotated=rotated
            photo.mirrored=mirrored
            photo.save()

    im.close()

def store_xmp_data(photo):
    xmp=libxmp.utils.file_to_dict(photo.full_path)
    for k,val in xmp.items():
        print(k)

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

        thumb_fname=os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir,fname+".jpeg")
        os.makedirs(os.path.join(models.PHOTO_ARCHIVE_THUMB,reldir),exist_ok=True)

        try:
            im = Image.open(photo_path)
            im.thumbnail( (128,128) )
            im.save(thumb_fname, "JPEG")
            im.close()
        except IOError:
            print("cannot create thumbnail for", photo_path)

        stat=os.stat(photo_path)
        dt=datetime.datetime.utcfromtimestamp(stat.st_mtime).replace(tzinfo=pytz.utc)

        im = Image.open(photo_path)
        imgformat,created=models.ImageFormat.objects.get_or_create(name=im.format,description=im.format_description)

        mimetype=magic.from_file(photo_path, mime=True)
        photo,created=models.Photo.objects.get_or_create(full_path=photo_path,
                                                         defaults={
                                                             "thumb_path": thumb_fname,
                                                             "width": im.width,
                                                             "height": im.height,
                                                             "format": imgformat,
                                                             "mode": im.mode,
                                                             "mimetype": mimetype,
                                                             "datetime": dt
                                                         })
        if not created:
            photo.thumb_path=thumb_fname
            photo.width=im.width
            photo.height=im.height
            photo.format=imgformat
            photo.mode=im.mode
            photo.mimetype=mimetype
            photo.datetime=dt
            photo.save()

        if "dpi" in im.info:
            dpi=str(im.info["dpi"])
            label,created=models.MetaLabel.objects.get_or_create(name="dpi")
            d,created=models.PhotoMetaDatum.objects.get_or_create(label=label,photo=photo,
                                                                  defaults={"value": dpi})
            if not created:
                d.value=dpi
                d.save()

        im.close()

        store_exif_data(photo)
        # store_xmp_data(photo)
