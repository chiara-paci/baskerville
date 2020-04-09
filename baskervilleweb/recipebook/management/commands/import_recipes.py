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

        archive=tarfile.open(name=fname,mode="r:bz2")

        m_base=archive.getmember("./base.json")
        fd=archive.extractfile(m_base)
        D=json.loads(fd.read().decode())
        for name,model in [ 
                ("tools",models.Tool),
                ("food_categories",models.FoodCategory),
                ("recipe_categories",models.RecipeCategory),
                ("retailers", models.Retailer),
                ("vendors", models.Vendor),
                ("recipe_labels",models.RecipeLabel),
        ]:
            for obj in D[name]: model.objects.deserialize(obj)

        for name,model in [ 
                ("step_sequences",models.StepSequence),
        ]:
            for tarinfo in archive.getmembers():
                if not tarinfo.name.startswith('./%s/' % name): continue
                fd=archive.extractfile(tarinfo)
                data=json.loads(fd.read().decode())
                model.objects.deserialize(data)


        for name,model in [ 
                ("measure_units",models.MeasureUnit),
                ("foods",models.Food),
                ("products",models.Product),
                ("ingredient",models.Ingredient),
                ("ingredient_groups",models.IngredientGroup),
                ("ingredient_alternatives",models.IngredientAlternative),
        ]:

            m_name=archive.getmember("./%s.json" % name)
            fd=archive.extractfile(m_name)
            D=json.loads(fd.read().decode())
            for obj in D:
                model.objects.deserialize(obj)
        
        for name,model in [ 
                ("recipes",models.Recipe),
                ("recipe_sets",models.RecipeSet),
        ]:
            for tarinfo in archive.getmembers():
                if not tarinfo.name.startswith('./%s/' % name): continue
                fd=archive.extractfile(tarinfo)
                data=json.loads(fd.read().decode())
                model.objects.deserialize(data)
            


        archive.close()
