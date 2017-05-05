# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import PasswordChangeForm,PasswordResetForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from django.forms.formsets import formset_factory

from foods.models import FrequentDiaryEntry,Product,MeasureUnit,Recipe

class DiaryForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(),empty_label=None)
    day=forms.ChoiceField(choices=[ ("today","today"),("yesterday","yesterday"),("tomorrow","tomorrow"),("other","other") ])
    time=forms.ChoiceField(choices=[ ("now","now"),("breakfast","breakfast"),("lunch","lunch"),("dinner","dinner"),
                                     ("morning","morning"),("afternoon","afternoon"),("other","other") ])
    entry_type=forms.ChoiceField(choices=[ ("frequent","frequent"),("recipe","recipe"),("product","product") ])
    
    other_day = forms.DateField(required=False)
    other_time = forms.TimeField(required=False)

    frequent_diary_entry = forms.ModelChoiceField(queryset=FrequentDiaryEntry.objects.all(),required=False)
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all(),required=False)
    product = forms.ModelChoiceField(queryset=Product.objects.all(),required=False)
    quantity = forms.FloatField(required=False,min_value=0)
    measure_unit = forms.ModelChoiceField(queryset=MeasureUnit.objects.all(),required=False)


DiaryFormset = formset_factory(DiaryForm)
