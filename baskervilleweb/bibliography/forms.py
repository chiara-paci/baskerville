from django import forms
from django.forms import extras
from django.forms.models import inlineformset_factory,modelformset_factory,BaseModelFormSet
from django.forms.formsets import BaseFormSet,formset_factory
from django.utils.safestring import mark_safe

from . import models

class ImmutableWidget(forms.widgets.HiddenInput):
    def render(self,name,value,attrs=None): 
        U=super(ImmutableWidget,self).render(name,value,attrs=attrs)
        return mark_safe(U+value)

class CategorizerForm(forms.ModelForm):
    parents = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"size":100}))

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if instance:
            initial = initial or {}
            initial['parents'] = instance.parents()

        super(CategorizerForm, self).__init__(initial=initial,instance=instance, *args, **kwargs)

    class Meta:
        model = models.Category
        fields = "__all__"
        widgets = {
            'name': ImmutableWidget(),
            }

    def save(self,commit=True):
        def remove_dup_space(S):
            S=S.strip()
            return " ".join(filter(bool,[x.strip() for x in S.split(" ")]))
            
        super(CategorizerForm, self).save(commit=commit)
        new_parents_names=list(map(remove_dup_space,self.cleaned_data["parents"].split(",")))
        deleted=[]
        unchanged=[]
        for old_rels in self.instance.parent_set.all():
            f_name=str(old_rels.parent.name)
            if not f_name in new_parents_names:
                deleted.append(f_name)
            else:
                unchanged.append(f_name)
        added=[x for x in new_parents_names if x not in unchanged]
        print(self.instance,deleted,added)
        for del_name in deleted:
            del_cat=models.Category.objects.get(name=del_name)
            models.CategoryRelation.objects.filter(parent=del_cat,child=self.instance).delete()
        for add_name in added:
            add_cat,created=models.Category.objects.get_or_create(name=add_name)
            models.CategoryRelation.objects.get_or_create(parent=add_cat,child=self.instance)


CategorizerFormset=modelformset_factory(models.Category, extra=0, 
                                        can_delete=True, 
                                        form=CategorizerForm)
class PublisherForm(forms.ModelForm):
    isbn = forms.CharField()
    class Meta:
        model = models.Publisher
        exclude = [ "addresses", "isbns" ]

class PublisherAddressForm(forms.Form):
    address = forms.ModelChoiceField(queryset=models.PublisherAddress.objects.all(),required=False)
    city_name = forms.CharField(required=False)
    state = forms.ModelChoiceField(queryset=models.PublisherState.objects.all(),required=False)
    state_name = forms.CharField(required=False)
    
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        if self.forms:
            self.forms[0].empty_permitted = False

PublisherAddressFormSet = formset_factory(PublisherAddressForm,extra=2,formset=RequiredFormSet)

class AuthorForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Author

class AuthorNameForm(forms.Form):
    name_type = forms.ModelChoiceField(queryset=models.NameType.objects.all(),required=False)
    value = forms.CharField(required=False)

AuthorNameFormSet = formset_factory(AuthorNameForm,extra=2,formset=RequiredFormSet,can_delete=True)
AuthorName0FormSet = formset_factory(AuthorNameForm,extra=0,formset=RequiredFormSet,can_delete=True)

class BookForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Book

class BookAuthorForm(forms.Form):
    author = forms.ModelChoiceField(queryset=models.Author.objects.all().select_related("cache"),required=False)
    author_role = forms.ModelChoiceField(queryset=models.AuthorRole.objects.all(),required=False)

BookAuthorFormSet = formset_factory(BookAuthorForm,extra=2,can_delete=True)

class CategoriesForm(forms.Form):
    categories = forms.CharField(required=False)

class IsbnForm(forms.Form):
    elenco = forms.CharField(widget=forms.Textarea(attrs={"rows":20,"cols":20,"class":"fixed"}))

class IssueAuthorForm(BookAuthorForm):
    pos = forms.IntegerField()

class IssueChoiceForm(forms.ModelForm):
    selected = forms.BooleanField(required=False)

    class Meta:
        model = models.Issue
        fields = [ "number","title" ]
        widgets = {
            "number": ImmutableWidget(),
            "title": ImmutableWidget(),
            #"date": ImmutableWidget(),
        }

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if instance:
            initial = initial or {}
            initial['selected'] = False

        super(IssueChoiceForm, self).__init__(initial=initial,instance=instance, *args, **kwargs)

IssueChoiceFormset = modelformset_factory(models.Issue,form=IssueChoiceForm,extra=0)

class SimpleSearchForm(forms.Form):
    search = forms.CharField()

class AuthorChoiceForm(forms.Form):
    author = forms.ModelChoiceField(queryset=models.Author.objects.all()) #,required=False)

    # def __init__(self,initial=None, queryset=models.Author.objects.all(), *args, **kwargs):
    #     super(AuthorChoiceForm, self).__init__(initial=initial, *args, **kwargs)
    #     self.fields["author"].queryset=queryset

class HiddenForm(forms.Form):
    hidden = forms.CharField(required=False)
