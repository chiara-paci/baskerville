"""
Management utility to create superusers.
"""
import tarfile
import json
import os,pwd,grp,io,time

from django.utils.text import slugify
from django.core.management.base import BaseCommand, CommandError

from recipebook import models

def build_tarinfo(fname,data):
    data = data.encode('utf8')
    info = tarfile.TarInfo(name=fname)
    info.size = len(data)
    info.uid=os.getuid()
    info.gid=os.getgid()
    info.mode=0o644
    info.uname=pwd.getpwuid(os.getuid())[0] 
    info.gname=grp.getgrgid(os.getgid())[0]
    info.mtime=time.time()
    return info, io.BytesIO(data)

class Command(BaseCommand):
    help = 'Export recipe book'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            'fname',
            help='filename',
        )

    def handle(self, *args, **options):
        fname = options["fname"]

        archive=tarfile.open(name=fname,mode="w:bz2")

        D={}
        for name,model in [ 
                ("tools",models.Tool),
                ("food_categories",models.FoodCategory),
                ("recipe_categories",models.RecipeCategory),
                ("retailers", models.Retailer),
                ("vendors", models.Vendor),
                ("recipe_labels",models.RecipeLabel),
        ]:
            D[name]=[ obj.__serialize__() for obj in model.objects.all() ]
        info,bdata=build_tarinfo("./base.json",json.dumps(D))
        archive.addfile(info, bdata)

        for name,model in [ 
                ("measure_units",models.MeasureUnit),
                ("products",models.Product),
                ("ingredient",models.Ingredient),
                ("foods",models.Food),
                ("ingredient_groups",models.IngredientGroup),
                ("ingredient_alternatives",models.IngredientAlternative),
        ]:
            D=[ obj.__serialize__() for obj in model.objects.all() ]
            info,bdata=build_tarinfo("./%s.json" % name,json.dumps(D))
            archive.addfile(info, bdata)
        
        for name,model in [ 
                ("recipe_sets",models.RecipeSet),
                ("step_sequences",models.StepSequence),
                ("recipes",models.Recipe),
        ]:
            for obj in model.objects.all():
                label="%d-%s" % (obj.id,slugify(obj.name).replace("-","_"))
                D=obj.__serialize__()
                info,bdata=build_tarinfo("./%s/%s.json" % (name,label),
                                         json.dumps(D))
                archive.addfile(info, bdata)
            


        archive.close()
