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
        
        #print(dir(im))
        #print(im.format,im.format_description,im.size,im.width,im.height,im.info,im.mode)
        
        imgformat,created=models.ImageFormat.objects.get_or_create(name=im.format,description=im.format_description)

        mimetype=magic.from_file(photo, mime=True)
        image,created=models.Photo.objects.get_or_create(full_path=photo,
                                                         defaults={
                                                             "thumb_path": thumb_fname,
                                                             "width": im.width,
                                                             "height": im.height,
                                                             "format": imgformat,
                                                             "mode": im.mode,
                                                             "mimetype": mimetype
                                                         })
        if not created:
            image.thumb_path=thumb_fname
            image.width=im.width
            image.height=im.height
            image.format=imgformat
            image.mode=im.mode
            image.mimetype=mimetype
            image.save()

        dpi=str(im.info["dpi"])
        label,created=models.MetaLabel.objects.get_or_create(name="dpi")
        d,created=models.PhotoMetaDatum.objects.get_or_create(label=label,photo=image,
                                                              defaults={"value": dpi})
        if not created:
            d.value=dpi
            d.save()

        if not hasattr(im,"_getexif"): 
            im.close()
            return

        im.close()
        im=open(photo,"rb")

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
            label,created=models.ExifLabel.objects.get_or_create( name=name,category=category,
                                                                  defaults={"type": datatype, "exif_id": tag_id} )
            d,created=models.ExifDatum.objects.get_or_create(photo=image,label=label,defaults={"value": val})
            if not created:
                d.value=val
                d.save()

            if label.name == "Orientation":
                # 1: 'Horizontal (normal)',
                # 2: 'Mirrored horizontal',
                # 3: 'Rotated 180',
                # 4: 'Mirrored vertical',
                # 5: 'Mirrored horizontal then rotated 90 CCW',
                # 6: 'Rotated 90 CW',
                # 7: 'Mirrored horizontal then rotated 90 CW',
                # 8: 'Rotated 90 CCW'
                if val.endswith("90 CCW"):
                    orientation="90 ccw"
                elif val.endswith("90 CW"):

        im.close()
