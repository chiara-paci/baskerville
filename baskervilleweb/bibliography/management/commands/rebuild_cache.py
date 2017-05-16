#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Author,Publication,PublisherIsbn,AuthorRelation,BookAuthorRelation,ArticleAuthorRelation,Book,CategoryTreeNode

class Command(BaseCommand):
    args = 'types'
    help = 'Update cache\ntypes: author_names, issn_crc, preferred_publisher, publication_years,isbn'

    def handle(self, *args, **options):
        types=args

        if len(args)==0:
            types=[ "author_names","issn_crc","preferred_publisher","publication_years","isbn","nodes" ]
        else:
            types=args

        if "author_names" in types:
            print("Author names")
            author_list=Author.objects.all()
            L=len(author_list)
            next_perc=10
            n=0
            for author in author_list:
                author.update_cache()
                n+=1
                if 100.0*float(n)/float(L) > next_perc:
                    print("    %2.2f%%" % (100*float(n)/float(L)))
                    next_perc+=10

        if "isbn" in types:
            print("ISBN")
            book_list=Book.objects.all()
            L=len(book_list)
            next_perc=10
            n=0
            for book in book_list:
                book.update_crc()
                n+=1
                if 100.0*float(n)/float(L) > next_perc:
                    print("    %2.2f%%" % (100*float(n)/float(L)))
                    next_perc+=10

        if "issn_crc" in types:
            print("ISSN crc")
            publication_list=Publication.objects.all()
            L=len(publication_list)
            next_perc=10
            n=0
            for publication in publication_list:
                publication.update_crc()
                n+=1
                if 100.0*float(n)/float(L) > next_perc:
                    print("    %2.2f%%" % (100*float(n)/float(L)))
                    next_perc+=10

        if "preferred_publisher" in types:
            print("Preferred Publisher")
            pub_isbn_list=PublisherIsbn.objects.all()
            L=len(pub_isbn_list)
            next_perc=10
            n=0
            for pub_isbn in pub_isbn_list:
                pub_isbn.update_preferred()
                n+=1
                if 100.0*float(n)/float(L) > next_perc:
                    print("    %2.2f%%" % (100*float(n)/float(L)))
                    next_perc+=10
            
        if "publication_years" in types:
            print("Publication Year")
            
            for rel in BookAuthorRelation.objects.all():
                rel.save()
            for rel in ArticleAuthorRelation.objects.all():
                rel.save()

            arel_list=AuthorRelation.objects.all()
            L=len(arel_list)
            next_perc=10
            n=0
            for arel in arel_list:
                arel.update_year()
                n+=1
                if 100.0*float(n)/float(L) > next_perc:
                    print("    %2.2f%%" % (100*float(n)/float(L)))
                    next_perc+=10
                
        if "nodes" in types:
            for node in CategoryTreeNode.objects.all():
                node.save()
