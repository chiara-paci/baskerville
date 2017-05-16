import re
import unittest
from unittest import skip
from django.shortcuts import render,redirect
from django.urls import reverse
from django.db.models.query import QuerySet

#from unittest.mock import patch,Mock

from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model
from django.core.paginator import Page,Paginator

User = get_user_model()

from .. import views
from .. import models
from .. import forms

BASE_URL="/bibliography"

import random,string

def random_string(L=0):
    if not L:
        L=random.choice(list(range(3,50)))
    return ''.join(random.choice(string.lowercase) for x in range(L))

def random_year(ymin=1900,ymax=2017):
    return random.choice(list(range(ymin,ymax)))

class InitialDataTest(TestCase):
    ## NameTypes
    ## NameFormats
    ## NameFormatCollection
    ## authorivari

    def test_publisher_isbn_senza(self):
        isbn=models.PublisherIsbn.objects.get(isbn="SENZA") # must not raise
        pub=models.Publisher.objects.get(name="-")
        self.assertEqual(isbn.preferred,pub)
        self.assertIn(isbn,pub.isbns.all())

    def test_name_types(self):
        L=models.NameType.objects.all().count()
        self.assertGreater(L,0)

    def test_author_roles(self):
        L=models.AuthorRole.objects.all().count()
        self.assertGreater(L,0)

    def test_name_formats(self):
        L=models.NameFormat.objects.all().count()
        self.assertGreater(L,0)
        aavv_nf=models.NameFormat.objects.get(label="aavv")              # not raise
        aavv_nf_ord=models.NameFormat.objects.get(label="aavv_ordering") # not raise

    def test_name_format_collections(self):
        L=models.NameFormatCollection.objects.all().count()
        self.assertGreater(L,0)
        aavv_fc=models.NameFormatCollection.objects.get(label="aavv")    # not raise
        aavv_nf=models.NameFormat.objects.get(label="aavv")              # not raise
        aavv_nf_ord=models.NameFormat.objects.get(label="aavv_ordering") # not raise
        self.assertEqual(aavv_fc.long_format,aavv_nf)        
        self.assertEqual(aavv_fc.short_format,aavv_nf)
        self.assertEqual(aavv_fc.list_format,aavv_nf)        
        self.assertEqual(aavv_fc.ordering_format,aavv_nf_ord)

    def test_author_aavv(self):
        L=models.Author.objects.all().count()
        self.assertGreater(L,0)
        aavv_fc=models.NameFormatCollection.objects.get(label="aavv")    # not raise
        author=models.Author.objects.get(format_collection=aavv_fc)
        person=models.Person.objects.get(format_collection=aavv_fc)
