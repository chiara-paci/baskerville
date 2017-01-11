import re
import unittest
from unittest import skip
from unittest.mock import patch,Mock

from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model

User = get_user_model()

from .. import views
from .. import models
from .. import forms

class HomePageTest(TestCase):
    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'bibliography/index.html')  

    # maxDiff=None

    # def assertEqualHtml(self,html_a,html_b):
    #     csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
    #     html_a=re.sub(csrf_regex, '<input type="hidden" name="csrfmiddlewaretoken" value="">', html_a)
    #     html_b=re.sub(csrf_regex, '<input type="hidden" name="csrfmiddlewaretoken" value="">', html_b)
    #     self.assertMultiLineEqual(html_a,html_b)

    # def test_home_page_renders_home_template(self):
    #     response = self.client.get('/')
    #     self.assertTemplateUsed(response, 'writing/home.html')  

    # def test_home_page_uses_section_form(self):
    #     response = self.client.get('/')
    #     self.assertIsInstance(response.context['form'], forms.SectionForm)

    # def test_for_invalid_input_renders_home_template(self):
    #     response = self.client.post('/writing/new', data={'text': ''})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'writing/home.html')
