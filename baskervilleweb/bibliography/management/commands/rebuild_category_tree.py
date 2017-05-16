#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from bibliography.models import Category,CategoryRelation,CategoryTreeNode,Book

def log_write(fd,msg):
    msg=msg.encode('utf-8')
    if fd:
        fd.write(msg)

class Command(BaseCommand):
    args = 'types'
    help = 'Update cache\ntypes: author_names, issn_crc, preferred_publisher, publication_years'

    def handle(self, *args, **options):

        if len(args)>=1:
            fname=args[0]
            fd=open(fname,"w")
        else:
            fd=None

        CategoryTreeNode.objects.all().delete()

        for cat in Category.objects.all():
            obj=CategoryTreeNode.objects.create_category(cat)
            print("Created: %s" % str(obj))
            log_write(fd,"Created: %s\n" % str(obj))

        for catrel in CategoryRelation.objects.all():
            print(catrel)
            log_write(fd,str(catrel))
            log_write(fd,"\n")
            obj_list=CategoryTreeNode.objects.add_child_category(catrel.parent,catrel.child)
            for action,obj in obj_list:
                log_write(fd,"    ")
                log_write(fd,str(action))
                log_write(fd," "+str(obj)+"\n")
        
        #CategoryTreeNode.objects.filter(is_category=False).delete()
        for catrel in Book.categories.through.objects.all():
            print(catrel.category,"/",catrel.book)
            log_write(fd,str(catrel.category)+"/")
            log_write(fd,str(catrel.book))
            log_write(fd,"\n")
            obj_list=CategoryTreeNode.objects.add_category_relation(catrel.category,catrel.book)
            for action,obj in obj_list:
                log_write(fd,"    ")
                log_write(fd,str(action))
                log_write(fd," "+str(obj))
                log_write(fd,"\n")

        if fd:
            fd.close()

        for node in CategoryTreeNode.objects.all():
            node.save()
