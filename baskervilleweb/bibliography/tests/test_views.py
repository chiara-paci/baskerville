import re
import unittest
import math
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
from .. import booksearch

from .base import *

BASE_URL="/bibliography"

import random,string

@skip
class ProvaTest(TestCase):

    def test_prova(self):
        format_c=random.choice(models.NameFormatCollection.objects.all())
        print(format_c)
        print(format_c.fields)
        kwargs={}
        for k in format_c.fields:
            kwargs[k]=random_string().capitalize()
        author=models.Author.objects.create_by_names(format_c,**kwargs)
        print(author)


class TemplateViewTestMixin(object):
    template_name=""
    page_id=""
    content_type="text/html; charset=utf-8"
    status=200

    def get_response(self):
        return self.client.get(reverse(self.page_id))

    def test_status(self):
        response=self.get_response()
        self.assertEqual(response.status_code, self.status)

    def test_renders_template(self):
        response=self.get_response()
        if self.template_name:
            self.assertTemplateUsed(response,self.template_name)  
        else:
            self.assertTemplateNotUsed(response,self.template_name)  

    def test_content_type(self):
        response=self.get_response()
        self.assertEqual(response["Content-type"],self.content_type)

class ListViewTestMixin(TemplateViewTestMixin):
    page_id=""
    template_name=""
    queryset=None
    context_object_list="object_list"

    def test_context_object_list(self):
        response=self.get_response()
        response_qset=response.context[self.context_object_list]
        self.assertEqual(list(self.queryset),list(response_qset))

class PaginatedListViewTestMixin(ListViewTestMixin):
    paginate_by=100

    def create_random_object(self): return None

    def get_response_pagination(self,num_objects):
        for n in range(0,num_objects):
            self.create_random_object()
        return self.get_response()

    def test_context_is_paginated(self):
        response=self.get_response()
        self.assertIsInstance(response.context['is_paginated'], bool)

    def test_context_page_obj(self):
        response=self.get_response()
        self.assertIsInstance(response.context['page_obj'], Page)

    def test_context_page_obj_paginator(self):
        response=self.get_response()
        self.assertIsInstance(response.context['page_obj'].paginator, Paginator)

    def test_paginator_per_page(self):
        response=self.get_response()
        self.assertEqual(response.context['page_obj'].paginator.per_page,self.paginate_by)

    def test_paginate_by_lower(self):
        response=self.get_response_pagination(self.paginate_by-1)
        self.assertEqual(response.context['page_obj'].paginator.num_pages,1)

    def test_paginate_by_upper(self):
        N=random.choice(list(range(2,10)))
        L=random.choice(list(range(self.paginate_by+1,N*self.paginate_by)))
        num_pages=int(math.ceil(L/float(self.paginate_by)))
        response=self.get_response_pagination(L)
        self.assertEqual(response.context['page_obj'].paginator.num_pages,num_pages)


class DetailViewTestMixin(TemplateViewTestMixin): 
    page_id=""
    template_name=""
    context_object=""
    content_type="text/html; charset=utf-8"

    def create_random_object(self): return None

    def get_response(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response

    def get_response_and_object(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response,obj

    def test_context_object(self):
        response,obj=self.get_response_and_object()
        self.assertEqual(obj, response.context[self.context_object])


class JsonDetailViewTestMixin(DetailViewTestMixin):
    content_type='application/json; charset=utf8'

#####

class RootTest(TestCase,TemplateViewTestMixin):
    template_name="bibliography/index.html"
    page_id="bibliography:index"

class CategoriesTest(TestCase,ListViewTestMixin):
    page_id="bibliography:categories"
    template_name="bibliography/categorytreenode_list.html"
    queryset=models.CategoryTreeNode.objects.filter(level=0)
    context_object_list="categorytreenode_list"
    
###

class BookMixin(object):
    context_object="book"
    context_object_list="book_list"
    
    def create_random_object(self):
        publisher=models.Publisher.objects.create(name=random_string())
        book=models.Book.objects.create(isbn_ced=random_string(L=4),
                                        isbn_book=random_string(L=5),
                                        title=random_string(),
                                        year=random_year(),
                                        publisher=publisher)
        return book

    def create_random_data(self):
        publisher=models.Publisher.objects.create(name=random_string())
        author_role=random.choice(models.AuthorRole.objects.all())
        format_c=random.choice(models.NameFormatCollection.objects.all())
        kwargs={}
        for k in format_c.fields:
            kwargs[k]=random_string().capitalize()
        author=models.Author.objects.create_by_names(format_c,**kwargs)
        ret={ "isbn_ced": random_string(L=4),
              "isbn_book": random_string(L=5),
              "title": random_string(),
              "year": random_year(),
              "publisher": publisher.id,
              "author-TOTAL_FORMS": 1,
              "author-INITIAL_FORMS": 0,
              "author-MAX_NUM_FORMS": 3,
              "author-0-author": author.id,
              "author-0-author_role": author_role.id,
        }
        return ret


    def create_random_invalid_data(self):
        ret={
            "author-TOTAL_FORMS": 0,
            "author-INITIAL_FORMS": 0,
            "author-MAX_NUM_FORMS": 3,
        }
        return ret

class BooksCategorizerTest(TestCase,BookMixin,PaginatedListViewTestMixin):
    page_id="bibliography:books-categorizer"
    template_name="bibliography/book_categorizer.html"
    queryset=models.Book.objects.all()

class BookDetailTest(TestCase,BookMixin,DetailViewTestMixin):
    page_id="bibliography:book-detail"
    template_name="bibliography/book_detail.html"

class PostTemplateViewTestMixin(TemplateViewTestMixin):
    page_id=""
    template_name=""
    content_type="text/html; charset=utf-8"
    status=200
    template_name_ok=""
    content_type_ok="text/html; charset=utf-8"
    status_ok=200
    template_name_no=""
    content_type_no="text/html; charset=utf-8"
    status_no=200

    def post_valid(self):
        response=self.client.post(reverse(self.page_id),data=self.create_random_data())
        return response

    def post_invalid(self):
        response=self.client.post(reverse(self.page_id),data=self.create_random_invalid_data())
        return response

    def test_valid_post_renders_template(self):
        response=self.post_valid()
        if self.template_name_ok:
            self.assertTemplateUsed(response,self.template_name_ok)  
        else:
            self.assertTemplateNotUsed(response,self.template_name_ok)  

    def test_valid_post_status(self):
        response=self.post_valid()
        self.assertEqual(response.status_code, self.status_ok)

    def test_valid_post_content_type(self):
        response=self.post_valid()
        self.assertEqual(response["Content-type"],self.content_type_ok)

    def test_invalid_post_renders_template(self):
        response=self.post_invalid()
        if self.template_name_no:
            self.assertTemplateUsed(response,self.template_name_no)  
        else:
            self.assertTemplateNotUsed(response,self.template_name_no)  

    def test_invalid_post_status(self):
        response=self.post_invalid()
        self.assertEqual(response.status_code, self.status_no)

    def test_invalid_post_content_type(self):
        response=self.post_invalid()
        self.assertEqual(response["Content-type"],self.content_type_no)

class CreateViewTestMixin(PostTemplateViewTestMixin):
    model=None
    form=None
    
    def test_form(self):
        response=self.get_response()
        self.assertIsInstance(response.context['form'], self.form)

    def test_valid_post_count(self):
        num_objs=self.model.objects.count()
        response=self.post_valid()
        new_num_objs=self.model.objects.count()
        self.assertEqual(new_num_objs, num_objs+1)
        
    def test_invalid_post_count(self):
        num_objs=self.model.objects.count()
        response=self.post_invalid()
        new_num_objs=self.model.objects.count()
        self.assertEqual(new_num_objs, num_objs)
        
    def test_invalid_post_form(self):
        response=self.post_invalid()
        self.assertIsInstance(response.context['form'], self.form)

class BookCreateTest(TestCase,BookMixin,CreateViewTestMixin):
    page_id="bibliography:book-create"
    template_name="bibliography/book_form.html"
    template_name_ok="bibliography/book_detail.html"
    template_name_no="bibliography/book_form.html"
    model=models.Book
    form=forms.BookForm

    def test_author_formset(self):
        obj=self.create_random_object()
        response=self.get_response()
        self.assertIsInstance(response.context['author_formset'], forms.BookAuthorFormSet)
        self.assertEqual(response.context['author_formset'].prefix,"author")

    def test_invalid_post_author_formset(self):
        obj=self.create_random_object()
        response=self.post_invalid()
        self.assertIsInstance(response.context['author_formset'], forms.BookAuthorFormSet)
        self.assertEqual(response.context['author_formset'].prefix,"author")

class JsonBookCreateTest(BookCreateTest):
    page_id="bibliography:json-book-create"
    status_no=400
    content_type_ok="application/json"
    content_type_no="application/json"
    template_name_ok="bibliography/book_detail.json"
    template_name_no=""
    
    def test_invalid_post_author_formset(self): pass

    def test_invalid_post_form(self): pass

class BookListAlphaTest(TestCase,BookMixin,ListViewTestMixin):
    page_id="bibliography:book-list-alpha"
    template_name="bibliography/book_list.html"
    queryset=models.Book.objects.isbn_alpha()

class JsonBookDetailTest(TestCase,BookMixin,JsonDetailViewTestMixin):
    page_id="bibliography:json-book-detail"
    template_name="bibliography/book_detail.json"


###

class AuthorMixin(object):
    context_object="author"
    context_object_list="author_list"
    
    def create_random_object(self):
        format_c=random.choice(models.NameFormatCollection.objects.all())
        kwargs={}
        for k in format_c.fields:
            kwargs[k]=random_string().capitalize()
        author=models.Author.objects.create_by_names(format_c,**kwargs)
        return author

    def create_random_data(self):
        format_c=random.choice(models.NameFormatCollection.objects.all())
        ret={ "format_collection": format_c.id,
              "name-TOTAL_FORMS": len(format_c.fields),
              "name-INITIAL_FORMS": 0,
              "name-MAX_NUM_FORMS": len(format_c.fields) }
        for n in range(0,len(format_c.fields)):
            ntype,created=models.NameType.objects.get_or_create(label=format_c.fields[n])
            val=random_string().capitalize()
            ret["name-"+str(n)+"-name_type"]=ntype.id
            ret["name-"+str(n)+"-value"]=val
        return ret

    def create_random_invalid_data(self):
        ret={
            "name-TOTAL_FORMS": 0,
            "name-INITIAL_FORMS": 0,
            "name-MAX_NUM_FORMS": 3,
        }
        return ret



class CatalogTest(TestCase,AuthorMixin,PaginatedListViewTestMixin):
    page_id="bibliography:catalog"
    template_name="bibliography/author_list.html"
    queryset=models.Author.objects.all()
    paginate_by=63

class AuthorDetailTest(TestCase,AuthorMixin,DetailViewTestMixin):
    page_id="bibliography:author-detail"
    template_name="bibliography/author_detail.html"

class AuthorListTest(TestCase,AuthorMixin,PaginatedListViewTestMixin):
    page_id="bibliography:author-list"
    template_name="bibliography/author_list.html"
    queryset=models.Author.objects.all()
    paginate_by=50


class JsonAuthorDetailTest(TestCase,AuthorMixin,JsonDetailViewTestMixin):
    page_id="bibliography:json-author-detail"
    template_name="bibliography/author_detail.json"

class AuthorCreateTest(TestCase,AuthorMixin,CreateViewTestMixin):
    page_id="bibliography:author-create"
    template_name="bibliography/author_form.html"
    template_name_ok="bibliography/author_detail.html"
    template_name_no="bibliography/author_form.html"
    model=models.Author
    form=forms.AuthorForm

    def test_name_formset(self):
        response=self.get_response()
        self.assertIsInstance(response.context['name_formset'], forms.AuthorNameFormSet)
        self.assertEqual(response.context['name_formset'].prefix,"name")

    def test_invalid_post_name_formset(self):
        response=self.post_invalid()
        self.assertIsInstance(response.context['name_formset'], forms.AuthorNameFormSet)
        self.assertEqual(response.context['name_formset'].prefix,"name")


class JsonAuthorCreateTest(AuthorCreateTest):
    page_id="bibliography:json-author-create"
    status_no=400
    content_type_ok="application/json"
    content_type_no="application/json"
    template_name_ok="bibliography/author_detail.json"
    template_name_no=""
    
    def test_invalid_post_name_formset(self): pass

    def test_invalid_post_form(self): pass

###

class PublisherMixin(object):
    context_object="publisher"
    context_object_list="object_list"
    
    def create_random_object(self):
        publisher=models.Publisher.objects.create(name=random_string())
        return publisher

    def create_random_data(self):
        ret={ "name": random_string(),
              "isbn": random_string(4),
              "url": "-",
              "address-TOTAL_FORMS": 0,
              "address-INITIAL_FORMS": 0,
              "address-MAX_NUM_FORMS": 0 }
        return ret

    def create_random_invalid_data(self):
        ret={
            "address-TOTAL_FORMS": 0,
            "address-INITIAL_FORMS": 0,
            "address-MAX_NUM_FORMS": 3,
        }
        return ret

    
class PublisherDetailTest(TestCase,PublisherMixin,DetailViewTestMixin):
    page_id="bibliography:publisher-detail"
    template_name="bibliography/publisher_detail.html"

class JsonPublisherDetailTest(TestCase,PublisherMixin,JsonDetailViewTestMixin):
    page_id="bibliography:json-publisher-detail"
    template_name="bibliography/publisher_detail.json"

class PublisherListTest(TestCase,PublisherMixin,ListViewTestMixin):
    page_id="bibliography:publisher-list"
    template_name="bibliography/publisher_list.html"
    queryset=models.Publisher.objects.all()

class PublisherCreateTest(TestCase,PublisherMixin,CreateViewTestMixin):
    page_id="bibliography:publisher-create"
    template_name="bibliography/publisher_form.html"
    template_name_ok="bibliography/publisher_detail.html"
    template_name_no="bibliography/publisher_form.html"
    model=models.Publisher
    form=forms.PublisherForm

    def test_address_formset(self):
        response=self.get_response()
        self.assertIsInstance(response.context['address_formset'], forms.PublisherAddressFormSet)
        self.assertEqual(response.context['address_formset'].prefix,"address")

    def test_invalid_post_address_formset(self):
        response=self.post_invalid()
        self.assertIsInstance(response.context['address_formset'], forms.PublisherAddressFormSet)
        self.assertEqual(response.context['address_formset'].prefix,"address")

class JsonPublisherCreateTest(PublisherCreateTest):
    page_id="bibliography:json-publisher-create"
    status_no=400
    content_type_ok="application/json"
    content_type_no="application/json"
    template_name_ok="bibliography/publisher_detail.json"
    template_name_no=""
    
    def test_invalid_post_address_formset(self): pass

    def test_invalid_post_form(self): pass

###
    
class PublisherIsbnListTest(TestCase,ListViewTestMixin):
    page_id="bibliography:publisherisbn-list"
    template_name="bibliography/publisherisbn_list.html"
    queryset=models.PublisherIsbn.objects.all()
    
class PublisherIsbnAlphaTest(TestCase,ListViewTestMixin):
    page_id="bibliography:publisherisbn-alpha"
    template_name="bibliography/publisherisbn_list.html"
    queryset=models.PublisherIsbn.objects.isbn_alpha()

class BookSerieWithoutIsbnTest(TestCase,ListViewTestMixin):
    page_id="bibliography:book-serie-without-isbn"
    template_name="bibliography/bookseriewithoutisbn_list.html"
    queryset=models.BookSerieWithoutIsbn.objects.all()
    
class NameFormatCollectionListTest(TestCase,ListViewTestMixin):
    page_id="bibliography:nameformatcollection-list"
    template_name="bibliography/nameformatcollection_list.html"
    queryset=models.NameFormatCollection.objects.all()

###

class PublicationMixin(object):
    context_object="publication"
    context_object_list="object_list"
    
    def create_random_object(self):
        publisher=models.Publisher.objects.create(name=random_string())

        pub=models.Publication.objects.create(issn=random_string(7),publisher=publisher,
                                              title=random_string(),
                                              volume_type=random.choice(models.VolumeType.objects.all()))
        return pub

class PublicationDetailTest(TestCase,PublicationMixin,DetailViewTestMixin):
    page_id="bibliography:publication-detail"
    template_name="bibliography/publication_detail.html"

    def test_add_author_form(self):
        obj=self.create_random_object()
        response=self.get_response()
        self.assertIsInstance(response.context['add_author_form'], forms.SimpleSearchForm)
    
class PublicationListTest(TestCase,PublicationMixin,ListViewTestMixin):
    page_id="bibliography:publication-list"
    template_name="bibliography/publication_list.html"
    queryset=models.Publication.objects.all()
    
class PublicationListAlphaTest(TestCase,PublicationMixin,ListViewTestMixin):
    page_id="bibliography:publication-list-alpha"
    template_name="bibliography/publication_list.html"
    queryset=models.Publication.objects.issn_alpha()
    
### category

class CategoryMixin(object):
    context_object_list="child_list"
    context_object="child"

    def create_random_object(self):
        category=models.Category.objects.create(name=random_string())
        return category

    def create_random_child(self,obj):
        category=models.Category.objects.create(name=random_string())
        models.CategoryRelation.objects.create(parent=obj,child=category)
        return category

class CategoryCategorizerViewTest(TestCase,CategoryMixin,PaginatedListViewTestMixin):
    page_id="bibliography:categories-categorizer"
    template_name="bibliography/category_categorizer.html"
    queryset=models.Category.objects.all()
    context_object_list="child_list"
    paginate_by=100

class CategoryCategorizerBranchViewTest(CategoryCategorizerViewTest):
    page_id="bibliography:categories-categorizer-branch"

    def get_response(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response

    def get_response_pagination(self,num_objects):
        obj=self.create_random_object()
        for n in range(0,num_objects):
            self.create_random_child(obj)
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response

    def get_response_and_object(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response,obj
    
    def test_context_object_list(self):
        response,obj=self.get_response_and_object()
        response_qset=response.context[self.context_object_list]
        queryset=models.Category.objects.all_in_branch(obj.id)
        self.assertEqual(list(queryset),list(response_qset))

###

class BooksInsertViewTest(TestCase,PostTemplateViewTestMixin):
    template_name="bibliography/isbn_form.html"
    page_id="bibliography:insert"
    template_name_ok="bibliography/insert_tool.html"
    template_name_no="bibliography/isbn_form.html"

    form=forms.IsbnForm

    def create_random_data(self): 
        isbn_ced=random_string(3).upper()
        isbn_book=random_string(6).upper()
        isbn="978"+isbn_ced+isbn_book+"Y"
        obj=models.RepositoryCacheBook.objects.create(isbn=isbn,publisher=random_string(30),
                                                      year=random_year(),title=random_string(50),city=random_string(15))
        return {"elenco": isbn_ced+"-"+isbn_book}

    def create_random_invalid_data(self): 
        return {}

    def test_form(self):
        response=self.get_response()
        self.assertIsInstance(response.context['form'], self.form)

    def test_invalid_post_form(self):
        response=self.post_invalid()
        self.assertIsInstance(response.context['form'], self.form)

    def check_valid_post_context_type_list(self,label,types=[str,str]):
        response=self.post_valid()
        self.assertIsInstance(response.context[label], list)
        if not response.context[label]: return
        for val in response.context[label]:
            self.assertIn(type(val),types)

    def check_valid_post_context_new_list(self,label,form_type,formset_type):
        response=self.post_valid()
        self.assertIsInstance(response.context[label], list)
        if not response.context[label]: return
        for val1,val2,v_form,v_formset in response.context[label]:
            self.assertIn(type(val1),[str,str])
            self.assertIn(type(val2),[str,str])
            self.assertIsInstance(v_form,form_type)
            self.assertIsInstance(v_formset,formset_type)

    def test_valid_post_context_new_book_list(self):
        self.check_valid_post_context_new_list("new_book_list",forms.BookForm, forms.BookAuthorFormSet)

    def test_valid_post_context_new_author_list(self):
        self.check_valid_post_context_new_list("new_author_list",forms.AuthorForm, forms.AuthorNameFormSet)
        
    def test_valid_post_context_new_publisher_list(self):
        self.check_valid_post_context_new_list("new_publisher_list",forms.PublisherForm, forms.PublisherAddressFormSet)
        
    def test_valid_post_context_isbn_list(self):
        self.check_valid_post_context_type_list("isbn_list")
        
    def test_valid_post_context_unseparable(self):
        self.check_valid_post_context_type_list("unseparable")
        
    def test_valid_post_context_old_book_list(self):
        self.check_valid_post_context_type_list("old_book_list",[booksearch.TemporaryBook])
        
    def test_valid_post_context_suspended_book_list(self):
        self.check_valid_post_context_type_list("suspended_book_list",[booksearch.TemporaryBook])

    def test_valid_post_context_old_publisher_list(self):
        self.check_valid_post_context_type_list("old_publisher_list",[booksearch.TemporaryPublisher])
        
    def test_valid_post_context_old_author_list(self):
        self.check_valid_post_context_type_list("old_author_list",[models.Author])

class AuthorSearchViewTest(TestCase,TemplateViewTestMixin):
    page_id="bibliography:author-search"

    template_name="bibliography/author_search.html"
    template_name_multiple="bibliography/author_list.html"
    template_name_not_found="bibliography/author_not_found.html"
    template_name_no="bibliography/author_search.html"

    form=forms.SimpleSearchForm

    content_type="text/html; charset=utf-8"
    status=200
    content_type_multiple="text/html; charset=utf-8"
    status_multiple=200
    content_type_not_found="text/html; charset=utf-8"
    status_not_found=200
    content_type_no="text/html; charset=utf-8"
    status_no=200

    ### get

    def test_form(self):
        response=self.get_response()
        self.assertIsInstance(response.context['form'], self.form)

    ### invalid post

    def create_random_invalid_data(self): 
        return {}

    def post_invalid(self):
        response=self.client.post(reverse(self.page_id),data=self.create_random_invalid_data())
        return response

    def test_invalid_post_renders_template(self):
        response=self.post_invalid()
        if self.template_name_no:
            self.assertTemplateUsed(response,self.template_name_no)  
        else:
            self.assertTemplateNotUsed(response,self.template_name_no)  

    def test_invalid_post_status(self):
        response=self.post_invalid()
        self.assertEqual(response.status_code, self.status_no)

    def test_invalid_post_content_type(self):
        response=self.post_invalid()
        self.assertEqual(response["Content-type"],self.content_type_no)

    def test_invalid_post_form(self):
        response=self.post_invalid()
        self.assertIsInstance(response.context['form'], self.form)

    ### valid not found

    def create_random_data_not_found(self): 
        return { "search": random_string() }

    def post_valid_not_found(self):
        response=self.client.post(reverse(self.page_id),data=self.create_random_data_not_found())
        return response

    def test_valid_post_not_found_renders_template(self):
        response=self.post_valid_not_found()
        self.assertTemplateUsed(response,self.template_name_not_found)  

    def test_valid_post_not_found_status(self):
        response=self.post_valid_not_found()
        self.assertEqual(response.status_code, self.status_not_found)

    def test_valid_post_not_found_content_type(self):
        response=self.post_valid_not_found()
        self.assertEqual(response["Content-type"],self.content_type_not_found)

    def test_valid_post_not_found_form(self):
        response=self.post_valid_not_found()
        self.assertIsInstance(response.context['form'], self.form)

    ### valid unique

    def create_random_data_unique(self): 
        format_c=random.choice(models.NameFormatCollection.objects.all())
        while not format_c.fields: 
            format_c=random.choice(models.NameFormatCollection.objects.all())
        kwargs={}
        for k in format_c.fields:
            kwargs[k]=random_string().capitalize()
        author=models.Author.objects.create_by_names(format_c,**kwargs)
        return {"search": list(kwargs.values())[0]},author

    def post_valid_unique(self):
        data,obj=self.create_random_data_unique()
        response=self.client.post(reverse(self.page_id),data=data)
        return response,obj

    def test_valid_post_unique_redirects_to_author_view(self):
        response,obj=self.post_valid_unique()
        self.assertRedirects(response, '/bibliography/author/%d' % (obj.id,))

    ### valid multiple found

    def create_random_data_multiple(self): 
        common_name=random_string(10)
        obj_id_list=[]
        for L in range(0,random.choice(list(range(2,20)))):
            format_c=random.choice(models.NameFormatCollection.objects.all())
            while not format_c.fields: 
                format_c=random.choice(models.NameFormatCollection.objects.all())
            kwargs={}
            kwargs[format_c.fields[0]]=common_name
            for k in format_c.fields[1:]:
                kwargs[k]=random_string().capitalize()
            author=models.Author.objects.create_by_names(format_c,**kwargs)
            obj_id_list.append(author.id)
        qset=models.Author.objects.filter(id__in=obj_id_list)
        return {"search": common_name},qset

    def post_valid_multiple(self):
        data,queryset=self.create_random_data_multiple()
        response=self.client.post(reverse(self.page_id),data=data)
        return response,queryset

    def test_valid_post_multiple_renders_template(self):
        response,queryset=self.post_valid_multiple()
        self.assertTemplateUsed(response,self.template_name_multiple)  

    def test_valid_post_multiple_status(self):
        response,queryset=self.post_valid_multiple()
        self.assertEqual(response.status_code, self.status_multiple)

    def test_valid_post_multiple_content_type(self):
        response,queryset=self.post_valid_multiple()
        self.assertEqual(response["Content-type"],self.content_type_multiple)

    def test_valid_post_multiple_context_object_list(self):
        response,queryset=self.post_valid_multiple()
        response_qset=response.context["object_list"]
        self.assertEqual(list(queryset),list(response_qset))


class AuthorInsertViewTest(AuthorSearchViewTest):
    page_id="bibliography:author-insert"

    template_name_not_found="bibliography/author_form.html"

    def test_valid_post_not_found_form(self):
        response=self.post_valid_not_found()
        self.assertIsInstance(response.context['form'], forms.AuthorForm)
        print(response.context["form"])

    def test_valid_post_not_found_formset(self):
        response=self.post_valid_not_found()
        self.assertIsInstance(response.context['name_formset'], forms.AuthorName0FormSet)

    def test_valid_post_not_found_action(self):
        response=self.post_valid_not_found()
        self.assertEqual(response.context['action'], reverse("bibliography:author-create"))

class PublicationIssuesAuthorChoiceViewTest(TestCase,PublicationMixin,TemplateViewTestMixin):
    page_id="bibliography:publication-issues-author-choice"
    template_name = "bibliography/publication_issues_author_choice.html"
    template_name_no = "bibliography/publication_issues_author_choice.html"
    template_name_ok = "bibliography/publication_issues_author_add.html"
    content_type="text/html; charset=utf-8"
    status=200
    content_type_ok="text/html; charset=utf-8"
    status_ok=200
    content_type_no="text/html; charset=utf-8"
    status_no=200

    form=forms.AuthorChoiceForm

    def get_response(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response

    def get_response_and_object(self):
        obj=self.create_random_object()
        response = self.client.get(reverse(self.page_id,kwargs={"pk": obj.id}))
        return response,obj

    def test_context_object(self):
        response,obj=self.get_response_and_object()
        self.assertEqual(obj, response.context[self.context_object])

    def create_random_data(self): 
        format_c=random.choice(models.NameFormatCollection.objects.all())
        kwargs={}
        for k in format_c.fields:
            kwargs[k]=random_string().capitalize()
        author=models.Author.objects.create_by_names(format_c,**kwargs)
        return { "author": author.id }

    def create_random_invalid_data(self): return {}

    def test_form(self):
        response=self.get_response()
        self.assertIsInstance(response.context['form'], self.form)

    def test_invalid_post_form(self):
        response,obj=self.post_invalid()
        self.assertIsInstance(response.context['form'], self.form)

    def test_invalid_post_context_object(self):
        response,obj=self.post_invalid()
        self.assertEqual(obj, response.context[self.context_object])

    def post_invalid(self):
        obj=self.create_random_object()
        response=self.client.post(reverse(self.page_id,kwargs={"pk": obj.id}),data=self.create_random_invalid_data())
        return response,obj

    def post_valid(self):
        obj=self.create_random_object()
        response=self.client.post(reverse(self.page_id,kwargs={"pk": obj.id}),data=self.create_random_data())
        return response,obj

    def test_valid_post_renders_template(self):
        response,obj=self.post_valid()
        if self.template_name_ok:
            self.assertTemplateUsed(response,self.template_name_ok)  
        else:
            self.assertTemplateNotUsed(response,self.template_name_ok)  

    def test_valid_post_status(self):
        response,obj=self.post_valid()
        self.assertEqual(response.status_code, self.status_ok)

    def test_valid_post_content_type(self):
        response,obj=self.post_valid()
        self.assertEqual(response["Content-type"],self.content_type_ok)

    def test_invalid_post_renders_template(self):
        response,obj=self.post_invalid()
        if self.template_name_no:
            self.assertTemplateUsed(response,self.template_name_no)  
        else:
            self.assertTemplateNotUsed(response,self.template_name_no)  

    def test_invalid_post_status(self):
        response,obj=self.post_invalid()
        self.assertEqual(response.status_code, self.status_no)

    def test_invalid_post_content_type(self):
        response,obj=self.post_invalid()
        self.assertEqual(response["Content-type"],self.content_type_no)

    def test_failed(self):
        self.fail("Manca il context")
