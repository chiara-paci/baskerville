import re
import unittest
import math
from unittest import skip

from .base import *

from .. import models
from .. import booksearch


class TesterTest(unittest.TestCase): 
    def test_book_on_repository_cache(self):
        isbn_ced=random_string(3).upper()
        isbn_book=random_string(6).upper()
        isbn="978"+isbn_ced+isbn_book+"Y"
        models.RepositoryCacheBook.objects.create(isbn=isbn,publisher=random_string(30),
                                                  year=random_year(),title=random_string(50),city=random_string(15))
        ret=booksearch.look_for([isbn_ced+"-"+isbn_book])
    
        print(ret)
