# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django import forms
from django.forms import extras
from django.forms.models import inlineformset_factory,modelformset_factory,BaseModelFormSet
from django.forms.formsets import BaseFormSet,formset_factory
from django.utils.safestring import mark_safe

from django.views.generic import TemplateView,ListView,View,CreateView
from bibliography.models import CategoryTreeNode,Category,CategoryRelation
from bibliography.models import Publisher,PublisherAddress,PublisherState,PublisherIsbn,PublisherAddressPublisherRelation
from bibliography.models import Author,NameType,AuthorNameRelation,NameFormatCollection
from bibliography.models import Book,BookAuthorRelation,AuthorRole
import bibliography.booksearch as booksearch

import json

class JsonCategoryNodesLinksView(View): 
    model = Category
    template_name = "bibliography/category_nodes_links.json"

    def get(self, request, *args, **kwargs):
        cat_maps={}
        root_maps={}

        roots=list(CategoryTreeNode.objects.roots())
        cats=list(Category.objects.all())

        max_num_objects=0

        n=0
        for root in roots:
            root_maps[root.node_id]=n
            max_num_objects=max(max_num_objects,root.num_objects)
            n+=1

        n=0
        category_list=[]
        for cat in cats:
            cat_maps[cat.id]=n
            branch=cat.my_branch_id()
            category_list.append( (cat,root_maps[branch],branch) )
            n+=1

        cat_rel=CategoryRelation.objects.all()

        rel_list=[]
        for rel in cat_rel:
            source=cat_maps[rel.father.id]
            target=cat_maps[rel.child.id]
            branch=rel.father.my_branch_id()
            rel_list.append( (source,target,root_maps[branch]) )

        return render(request, self.template_name, 
                      {"category_list": category_list,
                       "rel_list": rel_list,
                       "num_branch": len(roots),
                       "max_num_objects": max_num_objects,
                       "max_level": CategoryTreeNode.objects.max_level()},
                      content_type='application/json')

class CategoryChildrenView(ListView):
    model=Category
    paginate_by=100
    context_object_name="child_list"
    template_name="bibliography/category_categorizer.html"

    def get_queryset(self, *args, **kwargs):
        qset=super(CategoryChildrenView, self).get_queryset(*args, **kwargs)
        if not self.kwargs.has_key("pk"):
            return qset
        if not self.kwargs["pk"]:
            return qset
        father_id=self.kwargs["pk"]
        print father_id
        return Category.objects.all_in_branch(father_id)
        
        # father=Category.objects.get(pk=father_id)

        # children_ids=[]
        # for catnode in father.tree_nodes.all():
        #     print catnode
        #     L=catnode.branch()
        #     for cn in L:
        #         print cn
        #     children_ids+=map(lambda x: x.object_id,list(L))
        # children_ids=list(set(children_ids))
        # print children_ids
        # print 100 in children_ids
        # return Category.objects.filter(id__in=children_ids)

class CategoryTreeView(TemplateView):
    template_name="bibliography/category_tree.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryTreeView, self).get_context_data(**kwargs)
        obj_list = list(CategoryTreeNode.objects.all())
        context["category_tree"]=map(lambda x: x.get_desc("catroot"),obj_list)
        return context

class ImmutableWidget(forms.widgets.HiddenInput):
    def render(self,name,value,attrs=None): 
        U=super(ImmutableWidget,self).render(name,value,attrs=attrs)
        return mark_safe(U+value)

class CategorizerForm(forms.ModelForm):
    fathers = forms.CharField(required=False,widget=forms.widgets.TextInput(attrs={"size":100}))

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if instance:
            initial = initial or {}
            initial['fathers'] = instance.fathers()

        super(CategorizerForm, self).__init__(initial=initial,instance=instance, *args, **kwargs)

    class Meta:
        model = Category
        widgets = {
            'name': ImmutableWidget()
            }

    def save(self,commit=True):
        def remove_dup_space(S):
            S=S.strip()
            return " ".join(filter(bool,map(lambda x: x.strip(),S.split(" "))))
            
        super(CategorizerForm, self).save(commit=commit)
        new_fathers_names=map(remove_dup_space,self.cleaned_data["fathers"].split(","))
        deleted=[]
        unchanged=[]
        for old_rels in self.instance.father_set.all():
            f_name=unicode(old_rels.father.name)
            if not f_name in new_fathers_names:
                deleted.append(f_name)
            else:
                unchanged.append(f_name)
        added=filter(lambda x: x not in unchanged, new_fathers_names)
        print self.instance,deleted,added
        for del_name in deleted:
            del_cat=Category.objects.get(name=del_name)
            CategoryRelation.objects.filter(father=del_cat,child=self.instance).delete()
        for add_name in added:
            add_cat,created=Category.objects.get_or_create(name=add_name)
            CategoryRelation.objects.get_or_create(father=add_cat,child=self.instance)


CategorizerFormset=modelformset_factory(Category, extra=0, 
                                        can_delete=True, 
                                        form=CategorizerForm)

class CategorizerView(ListView):
    model = Category
    template_name = "bibliography/categorizer.html"

    def get_queryset(self, *args, **kwargs):
        qset=super(CategorizerView, self).get_queryset(*args, **kwargs)
        if not self.kwargs.has_key("pk"):
            return qset
        if not self.kwargs["pk"]:
            return qset
        father_id=self.kwargs["pk"]
        print father_id
        father=Category.objects.get(pk=father_id)

        children_ids=[]
        for catnode in father.tree_nodes.all():
            print catnode
            L=catnode.branch()
            for cn in L:
                print cn
            children_ids+=map(lambda x: x.object_id,list(L))
        children_ids=list(set(children_ids))
        print children_ids
        print 100 in children_ids
        return Category.objects.filter(id__in=children_ids)

    def get(self, request, *args, **kwargs):
        formset = CategorizerFormset(queryset=self.get_queryset())
        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = CategorizerFormset(request.POST,request.FILES,queryset=self.get_queryset())
        if formset.is_valid():
            formset.save()
            formset = CategorizerFormset(queryset=self.get_queryset())
            return render(request, self.template_name, {'formset': formset})
        return render(request, self.template_name, {'formset': formset})



class JsonTreeView(ListView): 
    model = CategoryTreeNode
    template_name="bibliography/category_tree_node.json"
    context_object_name="categorytreenode_list"

    def render_to_response(self, context, **kwargs):
        return super(JsonTreeView, self).render_to_response(context,content_type='application/json; charset=utf-8', **kwargs)

    def get_template_names(self):
        L=super(JsonTreeView, self).get_template_names()
        ret=map(lambda x: x.replace(".html",".json"),L)
        return(ret)

    def get_queryset(self):
        label_children=self.kwargs["label_children"].replace("_",":")
        level=int(self.kwargs["level"])
        q=super(JsonTreeView, self).get_queryset()
        return q.filter(node_id__istartswith=label_children+":",level=level)

    # def get_context_data(self,**kwargs):
    #     content_type_id=self.kwargs["content_type_id"]
    #     object_id=self.kwargs["object_id"]
    #     context=super(JsonTreeView,self).get_context_data(**kwargs)
    #     context["content_type_id"]=content_type_id
    #     context["object_id"]=object_id
    #     return context

### Create Publisher

class PublisherForm(forms.ModelForm):
    isbn = forms.CharField()
    class Meta:
        model = Publisher
        exclude = [ "addresses", "isbns" ]

class PublisherAddressForm(forms.Form):
    address = forms.ModelChoiceField(queryset=PublisherAddress.objects.all(),required=False)
    city_name = forms.CharField(required=False)
    state = forms.ModelChoiceField(queryset=PublisherState.objects.all(),required=False)
    state_name = forms.CharField(required=False)
    
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False

PublisherAddressFormSet = formset_factory(PublisherAddressForm,extra=2,formset=RequiredFormSet)

class PublisherCreateView(CreateView):
    form_class=PublisherForm
    model=Publisher
    template_name="bibliography/publisher_form.html"
    template_name_response="bibliography/publisher_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PublisherCreateView, self).get_context_data(**kwargs)
        context['address_formset'] = PublisherAddressFormSet(prefix="address")
        return context

    def post(self, request, *args, **kwargs):
        form = PublisherForm(request.POST)
        address_formset = PublisherAddressFormSet(request.POST,prefix="address")

        if not form.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'address_formset': address_formset})

        if not address_formset.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'address_formset': address_formset})

        publisher_obj=self.create_object(form,address_formset)
        return render(request, self.template_name_response, {"publisher": publisher_obj})
        
    def create_object(self,form,address_formset):
        isbn=form.cleaned_data["isbn"]
        name=form.cleaned_data["name"]
        full_name=form.cleaned_data["full_name"]
        alias=form.cleaned_data["alias"]
        note=form.cleaned_data["note"]
        url=form.cleaned_data["url"]
        publisher_obj,created=Publisher.objects.get_or_create(name=name,
                                                              defaults={ "full_name": full_name,
                                                                         "url": url,
                                                                         "note": note,
                                                                         "alias": alias })
        isbn_obj,created=PublisherIsbn.objects.get_or_create(isbn=isbn,defaults={"preferred":publisher_obj})

        if not created: 
            publisher_obj.alias=(isbn_obj.preferred!=publisher_obj)
            publisher_obj.save()

        publisher_obj.isbns.add(isbn_obj)

        address_obj_list=[]
        pos=-1
        for row_data in address_formset.cleaned_data:
            if not row_data: continue
            pos+=1
            print row_data
            address_obj=row_data["address"]
            if address_obj:
                address_obj_list.append((pos,address_obj))
                continue
            state_obj=row_data["state"]
            if not state_obj:
                state_name=row_data["state_name"]
                state_obj,created=PublisherState.objects.get_or_create(name=state_name)
            city_name=row_data["city_name"]
            address_obj,created=PublisherAddress.objects.get_or_create(city=city_name,state=state_obj)
            address_obj_list.append((pos,address_obj))

        for (pos,address_obj) in address_obj_list:
            PublisherAddressPublisherRelation.objects.get_or_create(address=address_obj,publisher=publisher_obj,pos=pos)

        return publisher_obj


class JsonPublisherCreateView(PublisherCreateView):
    form_class=PublisherForm
    model=Publisher
    template_name="bibliography/publisher_form.html"
    template_name_response="bibliography/publisher_detail.json"

    def post(self, request, *args, **kwargs):
        form = PublisherForm(request.POST)
        address_formset = PublisherAddressFormSet(request.POST,prefix="address")

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if not address_formset.is_valid():
            data["address_formset_errors"]=address_formset.errors
            data["address_form_errors"]=[]
            for form in address_formset:
                data["address_form_errors"].append({"instance": form.instance.id,"errors":form.errors})
        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')
        
        publisher_obj=self.create_object(form,address_formset)
        return render(request, self.template_name_response, 
                      {"publisher": publisher_obj},
                      content_type='application/json')

### Create Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author

class AuthorNameForm(forms.Form):
    name_type = forms.ModelChoiceField(queryset=NameType.objects.all(),required=False)
    value = forms.CharField(required=False)

AuthorNameFormSet = formset_factory(AuthorNameForm,extra=2,formset=RequiredFormSet)

class AuthorCreateView(CreateView):
    form_class=AuthorForm
    model=Author
    template_name="bibliography/author_form.html"
    template_name_response="bibliography/author_detail.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorCreateView, self).get_context_data(**kwargs)
        context['name_formset'] = AuthorNameFormSet(prefix="name")
        return context

    def post(self, request, *args, **kwargs):
        form = AuthorForm(request.POST)
        name_formset = AuthorNameFormSet(request.POST,prefix="name")

        if not form.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'name_formset': name_formset})

        if not name_formset.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'name_formset': name_formset})

        author_obj=self.create_object(form,name_formset)
        return render(request, self.template_name_response, {"author": author_obj})
        
    def create_object(self,form,name_formset):
        format_collection=form.cleaned_data["format_collection"]
        author_obj=Author(format_collection=format_collection)
        author_obj.save()

        for row_data in name_formset.cleaned_data:
            if not row_data: continue
            name_type=row_data["name_type"]
            value=row_data["value"]
            if name_type:
                name_obj,created=AuthorNameRelation.objects.get_or_create(author=author_obj,name_type=name_type,value=value)
        author_obj.update_cache()

        return author_obj

class JsonAuthorCreateView(AuthorCreateView):
    form_class=AuthorForm
    model=Author
    template_name="bibliography/author_form.html"
    template_name_response="bibliography/author_detail.json"

    def post(self, request, *args, **kwargs):
        form = AuthorForm(request.POST)
        name_formset = AuthorNameFormSet(request.POST,prefix="name")

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if not name_formset.is_valid():
            data["name_formset_errors"]=name_formset.errors
            data["name_form_errors"]=[]
            for form in name_formset:
                data["name_form_errors"].append({"instance": form.instance.id,"errors":form.errors})
        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')
        
        author_obj=self.create_object(form,name_formset)
        return render(request, self.template_name_response, 
                      {"author": author_obj},
                      content_type='application/json')


### Create Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book

class BookAuthorForm(forms.Form):
    author = forms.ModelChoiceField(queryset=Author.objects.all(),required=False)
    author_role = forms.ModelChoiceField(queryset=AuthorRole.objects.all(),required=False)

BookAuthorFormSet = formset_factory(BookAuthorForm,extra=2)

class BookCreateView(CreateView):
    form_class=BookForm
    model=Book
    template_name="bibliography/book_form.html"
    template_name_response="bibliography/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super(BookCreateView, self).get_context_data(**kwargs)
        context['author_formset'] = BookAuthorFormSet(prefix="author")
        return context

    def post(self, request, *args, **kwargs):
        form = BookForm(request.POST)
        author_formset = BookAuthorFormSet(request.POST,prefix="author")

        if not form.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'author_formset': author_formset})

        if not author_formset.is_valid():
            return render(request, self.template_name, 
                          {'form': form, 'author_formset': author_formset})

        book_obj=self.create_object(form,author_formset)
        return render(request, self.template_name_response, {"book": book_obj})
        
    def create_object(self,form,author_formset):
        isbn_ced=form.cleaned_data["isbn_ced"]
        isbn_book=form.cleaned_data["isbn_book"]
        title=form.cleaned_data["title"]
        year=form.cleaned_data["year"]
        publisher=form.cleaned_data["publisher"]
        book_obj,created=Book.objects.get_or_create(isbn_ced=isbn_ced,isbn_book=isbn_book,
                                                    defaults={"title": title, "year": year, "publisher": publisher })

        pos=0
        for row_data in author_formset.cleaned_data:
            if not row_data: continue
            author_role=row_data["author_role"]
            author=row_data["author"]
            rel_obj,created=BookAuthorRelation.objects.get_or_create(book=book_obj,author=author,
                                                                     defaults={"author_role":author_role,"pos":pos,"year":book_obj.year})
            pos+=1
        return book_obj

class JsonBookCreateView(BookCreateView):
    form_class=BookForm
    model=Book
    template_name="bibliography/book_form.html"
    template_name_response="bibliography/book_detail.json"

    def post(self, request, *args, **kwargs):
        form = BookForm(request.POST)
        author_formset = BookAuthorFormSet(request.POST,prefix="author")

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if not author_formset.is_valid():
            data["author_formset_errors"]=author_formset.errors
            data["author_form_errors"]=[]
            for form in author_formset:
                data["author_form_errors"].append({"instance": form.instance.id,"errors":form.errors})
        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')
        
        book_obj=self.create_object(form,author_formset)
        return render(request, self.template_name_response, 
                      {"book": book_obj},
                      content_type='application/json')

class CategoriesForm(forms.Form):
    categories = forms.CharField(required=False)

class JsonBookChangeCategoriesView(View):
    template_name_response="bibliography/book_detail.json"

    def post(self, request, *args, **kwargs):
        form = CategoriesForm(request.POST)

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')

        book_id=self.kwargs['pk']
        book_obj=Book.objects.get(id=book_id)

        categories_txt=form.cleaned_data["categories"].strip()
        categories=map(lambda x: x.strip().replace('.','.*'),categories_txt.split(";"))
        categories_objects=[]

        for cat in categories:
            L=Category.objects.filter(name__iregex=cat)
            if len(L)==0:
                cat_obj=Category.objects.create(name=cat)
            else:
                cat_obj=L[0]
            categories_objects.append(cat_obj)
        
        for cat_obj in book_obj.categories.all():
            if cat_obj in categories_objects: continue
            book_obj.categories.remove(cat_obj)

        for cat_obj in categories_objects:
            book_obj.categories.add(cat_obj)

        return render(request, self.template_name_response, 
                      {"book": book_obj},
                      content_type='application/json')

class JsonCategoryChangeFathersView(View):
    template_name_response="bibliography/category_detail.json"

    def post(self, request, *args, **kwargs):
        form = CategoriesForm(request.POST)

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')

        child_id=self.kwargs['pk']
        child_obj=Category.objects.get(id=child_id)

        fathers_txt=form.cleaned_data["categories"].strip()
        fathers=map(lambda x: x.strip().replace('.','.*'),fathers_txt.split(";"))
        fathers_objects=[]

        for cat in fathers:
            cat=cat.strip()
            if not cat: continue
            L=Category.objects.filter(name__iregex='^'+cat+'$')
            if len(L)==0:
                cat_obj=Category.objects.create(name=cat)
            else:
                cat_obj=L[0]
            fathers_objects.append(cat_obj)

        print fathers,fathers_objects
        
        for rel_obj in child_obj.father_set.all():
            print rel_obj
            if rel_obj.father in fathers_objects: continue
            print rel_obj
            rel_obj.delete()

        for cat_obj in fathers_objects:
            CategoryRelation.objects.get_or_create(child=child_obj,father=cat_obj)

        return render(request, self.template_name_response, 
                      {"category": child_obj},
                      content_type='application/json')




### Insert
class IsbnForm(forms.Form):
    elenco = forms.CharField(widget=forms.Textarea(attrs={"height":"200px","width":50}))

class BooksInsertView(View): 
    template_name_isbn = "bibliography/isbn_form.html"
    template_name_insert = "bibliography/insert_tool.html"

    def get(self, request, *args, **kwargs):
        form = IsbnForm()
        return render(request, self.template_name_isbn, {'form': form})

    def post(self, request, *args, **kwargs):
        form = IsbnForm(request.POST)
        if form.is_valid():
            elenco=form.cleaned_data["elenco"].strip()
            isbn_list=[]
            for r in elenco.split("\n"):
                r=r.strip()
                t=r.split(" ")
                isbn_list+=t
            params=booksearch.look_for(isbn_list)
            
            new_publisher_list=[]
            old_publisher_list=[]            
            n=0
            for pub in params["publisher_list"]:
                if pub.indb:
                    old_publisher_list.append(pub)
                    continue
                initial={ "isbn": pub.isbn_ced, "name": pub.name, "full_name": pub.name }
                pubform=PublisherForm(prefix="newpublisher"+str(n),initial=initial)
                initial=[]
                if pub.addresses_indb:
                    for adr in pub.addresses:
                        initial.append({"address":adr})
                else:
                    for adr in pub.addresses:
                        initial.append({"city_name":adr})
                pubadrsformset=PublisherAddressFormSet(prefix="newpublisher"+str(n)+"-address",initial=initial)
                new_publisher_list.append( (str(n),pub.name,pubform, pubadrsformset) )
                n+=1

            suspended_book_list=[]
            new_book_list=[]
            old_book_list=[]
            new_author_list=[]
            temp_author_list=[]
            old_author_list=[]

            n=0
            for book in params["book_list"]:
                if book.indb:
                    old_book_list.append(book)
                    continue
                suspended=False
                for role,pos,aut in book.authors:
                    if type(aut) not in [unicode,str]:
                        old_author_list.append(aut)
                        continue
                    temp_author_list.append(aut)
                    suspended=True
                if suspended:
                    suspended_book_list.append(book)
                    continue
                if type(book.publisher)!=Publisher:
                    suspended_book_list.append(book)
                    continue
                initial={ "isbn_ced": book.isbn_ced, "isbn_book": book.isbn_book, 
                          "title": book.title, "year": book.year, "publisher": book.publisher }
                bookform=BookForm(prefix="newbook"+str(n),initial=initial)
                initial=[]
                lauts=map(lambda x: (x[1],(x[0],x[2])),book.authors)
                lauts.sort()
                for pos,(role,author) in lauts:
                    aut_role=AuthorRole.objects.get(label=role)
                    initial.append({"author":author,"author_role":aut_role})
                bookauthorformset=BookAuthorFormSet(prefix="newbook"+str(n)+"-author",initial=initial)
                new_book_list.append( (str(n),book.isbn_10().replace("-","")+" "+book.title,bookform, bookauthorformset) )
                n+=1
            n=0
            for aut in temp_author_list:
                t=filter(lambda x: bool(x),map(lambda x: x.strip(),aut.strip().split(" ")))
                print t,len(t)
                initial=[]
                if len(t)==1:
                    lab_format="onename"
                    initial=[ {"name_type": "name", "value": t[0] } ]
                elif len(t)==2:
                    lab_format="western_twonames"
                    initial=[ {"name_type": "name", "value": t[0] },
                              {"name_type": "surname", "value": t[1] } ]
                else:
                    lab_format="western_threenames"
                    initial=[ {"name_type": "name", "value": t[0] },
                              {"name_type": "middle_name", "value": t[1] },
                              {"name_type": "surname", "value": " ".join(t[2:]) } ]
                format_collection=NameFormatCollection.objects.get(label=lab_format)
                for ini in initial:
                    ini["name_type"]=NameType.objects.get(label=ini["name_type"])
                autform=AuthorForm(prefix="newauthor"+str(n),initial={"format_collection":format_collection})
                autnamesformset=AuthorNameFormSet(prefix="newauthor"+str(n)+"-name",initial=initial)
                new_author_list.append( (str(n),aut,autform, autnamesformset) )
                n+=1

            params["new_book_list"]=new_book_list
            params["suspended_book_list"]=suspended_book_list
            params["old_book_list"]=old_book_list
            params["new_author_list"]=new_author_list
            params["old_author_list"]=old_author_list
            params["new_publisher_list"]=new_publisher_list
            params["old_publisher_list"]=old_publisher_list

            return render(request, self.template_name_insert, params)
        return render(request, self.template_name_isbn, {'form': form})

#### category graph

