import exifread
import dateutil.parser
import os,datetime,magic,pytz
from PIL import Image,ImageDraw,ImageFont

from django.contrib.staticfiles import finders


from archive import models

def store_asset(doc,asset_path,thumb_path):
    fname,ext=os.path.splitext(asset_path)
    ext=ext.lower()
    try:
        im = Image.open(asset_path)
        im.convert("RGB").thumbnail( (128,128),Image.LANCZOS )
        im.save(thumb_path, "JPEG")
        im.close()
    except IOError:

        font_path= finders.find('fonts/OpenSans-Bold-webfont.ttf')
        #searched_locations = finders.searched_locations
        im = Image.new('RGB', (128, 128), color = '#ffffff')
        draw = ImageDraw.Draw(im)

        X=4
        Y=19

        poly1=[(0,0),(0,90),(120,90),(120,45),(75,0)]
        poly1=[ (x+X,y+Y) for x,y in poly1 ]
        poly2=[(120,45),(75,45),(75,0)]
        poly2=[ (x+X,y+Y) for x,y in poly2 ]

        draw.polygon(
            poly1,
            fill='#e9f4ce',
            outline="#87a73b",
        )

        draw.polygon(poly2,fill='#87a73b')

        for x in range(15,75,10):
            draw.line( [ (x+X,10+Y),(x+X,45+Y) ], fill="#87a73b")

        fnt = ImageFont.truetype(font_path, 20)
        draw.text( (X+5,90-30+Y), ext, font=fnt,fill="#87a73b" )


        #draw.line((0, 0) + im.size, fill=128)
        #draw.line((0, im.size[1], im.size[0], 0), fill=128)
        
        # write to stdout

        im=im.rotate(90)
        im.save(thumb_path, "JPEG")

        #print("cannot create thumbnail for", asset_path)
        #return None
    
    stat=os.stat(asset_path)
    dt=datetime.datetime.utcfromtimestamp(stat.st_mtime).replace(tzinfo=pytz.utc)
    mimetype=magic.from_file(asset_path, mime=True)

    asset,created=models.DocumentAsset.objects.update_or_create(document=doc,
                                                                full_path=asset_path,
                                                                defaults={
                                                                    "thumb_path": thumb_path,
                                                                    "mimetype": mimetype,
                                                                    "datetime": dt
                                                                })
    return asset
    


def store_photo(photo_path,thumb_path):

    try:
        im = Image.open(photo_path)
        im.thumbnail( (128,128) )
        im.save(thumb_path, "JPEG")
        im.close()
    except IOError:
        print("cannot create thumbnail for", photo_path)
        return None

    stat=os.stat(photo_path)
    dt=datetime.datetime.utcfromtimestamp(stat.st_mtime).replace(tzinfo=pytz.utc)
    mimetype=magic.from_file(photo_path, mime=True)

    im = Image.open(photo_path)
    imgformat,created=models.ImageFormat.objects.get_or_create(name=im.format,description=im.format_description)

    photo,created=models.Photo.objects.get_or_create(full_path=photo_path,
                                                     defaults={
                                                         "thumb_path": thumb_path,
                                                         "width": im.width,
                                                         "height": im.height,
                                                         "format": imgformat,
                                                         "mode": im.mode,
                                                         "mimetype": mimetype,
                                                         "datetime": dt
                                                     })
    if not created:
        photo.thumb_path=thumb_path
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
    return photo


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

        if label.name in [ "DateTime", "DateTimeDigitized" ]:
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

