#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import os
import locale

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from bibliography.models import Category,Person,CategoryPersonRelation,NameFormatCollection

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        names=[]

        for label in [ "opere ","autobiografie di","biografie di","testi di","testi filosofici di"]:
            for cat in Category.objects.filter(name__istartswith=label):
                cat_name=cat.name.strip()
                t=cat.name.strip().split(" ")
                ind=0
                for n in range(0,len(t)):
                    if t[n] in ["di","del"]:
                        ind=n
                        break
                names.append( (cat,t[ind+1:]) )

        # for label in [ "onename" ]:
        #     format_collection_map[label]=NameFormatCollection.objects.get(label=label)

        # for label in [ "name","surname" ]:
        #     type_map[label]=NameType.objects.get(label=label)

        for cat,t in names:
            if CategoryPersonRelation.objects.filter(category=cat).exists():
                continue
            test=t[-1][1]
            if test.isdigit(): 
                t=t[:-1]

            # if len(t)==1:
            #     lab_format="onename"
            #     initial=[ {"name_type": "name", "value": t[0].capitalize() } ]
            # elif len(t)==2:
            #     if ( t[0]=="beato" and t[1]=="angelico" ) or ( t[0]=="el" and t[1]=="greco"): 
            #         lab_format="onename"
            #         initial=[ {"name_type": "name", "value": t[0].capitalize()+" "+t[1].capitalize() } ]
            #     else:
            #         x=t[0].split("-")
            #         name="-".join(map(lambda x: x.capitalize(),t[0].split("-")))
            #         surname="-".join(map(lambda x: x.capitalize(),t[1].split("-")))
                    
            #         lab_format="western_twonames"
            #         initial=[ {"name_type": "name", "value": name },
            #                   {"name_type": "surname", "value": surname } ]
            # else:
            #     continue
            #     lab_format="western_threenames"
            #     initial=[ {"name_type": "name", "value": t[0].capitalize() },
            #               {"name_type": "middle_name", "value": t[1].capitalize() },
            #               {"name_type": "surname", "value": u" ".join(t[2:]) } ]
            

            # print t
            # print "    ",lab_format
            
            # for name_dict in initial:
            #     print u"    ",name_dict["name_type"],name_dict["value"]

            print(t)
            for p in Person.objects.filter_by_name(" ".join(t)):
                print("    ",p)

        # print(sys.stdout.encoding)
        # print(sys.stdout.isatty())
        # print(locale.getpreferredencoding())
        # print(sys.getfilesystemencoding())
        # print(os.environ["PYTHONIOENCODING"])
        # print(chr(246), chr(9786), chr(9787))
        


