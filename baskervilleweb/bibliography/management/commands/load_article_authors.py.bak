#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Article,MigrAuthor,ArticleAuthorRelation,AuthorRole

class Command(BaseCommand):
    args = '<file_elenco>'
    help = 'Load categories'

    def handle(self, *args, **options):
        elenco=args[0]

        lista=[]
        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            t=map(lambda x: x.strip(),l.split("|"))
            if len(t)!=8: 
                print t
                continue

            issn_pub=t[0].strip()
            issn_num=t[1].strip()
            pages=t[2].strip()
            aut_cod=t[4].strip()
            aut_ind=t[5].strip()
            aut_role=t[6].strip()
            aut_pos=int(t[7].strip())
            t=pages.split("-")
            page_begin=t[0]
            page_end=t[1]

            if aut_cod=="A" and aut_ind=="0": continue

            try:
                migr_auth_obj=MigrAuthor.objects.get(cod=aut_cod,ind=aut_ind)
            except ObjectDoesNotExist, e:
                print "NE author:",aut_cod,aut_ind
                sys.exit()
            
            author_obj=migr_auth_obj.author

            try:
                article_obj=Article.objects.get(issue__volume__pubblication__issn=issn_pub,
                                                issue__issn_num=issn_num,
                                                page_begin=page_begin,page_end=page_end)
            except ObjectDoesNotExist, e:
                print "NE article:",issn_pub,issn_num,pages
                sys.exit()

            author_role,created=AuthorRole.objects.get_or_create(label=aut_role,
                                                                 defaults={"description":aut_role.capitalize()})


            if created:
                print "Created: ",author_role

            author_article_rel,created=ArticleAuthorRelation.objects.get_or_create(author=author_obj,article=article_obj,
                                                                                   author_role=author_role,
                                                                                   defaults={"pos":aut_pos})
            if created:
                print "Created: ",author_article_rel
                

        fd.close()

