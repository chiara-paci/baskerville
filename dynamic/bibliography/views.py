# -*- coding: utf-8 -*-

from django.shortcuts import render,redirect
from django.urls import reverse

from . import forms

from django.views.generic import TemplateView,ListView,View,CreateView,DetailView
from django.views.generic.detail import SingleObjectMixin

from bibliography.models import CategoryTreeNode,Category,CategoryRelation
from bibliography.models import Publisher,PublisherAddress,PublisherState,PublisherIsbn,PublisherAddressPublisherRelation
from bibliography.models import Author,NameType,PersonNameRelation,NameFormatCollection
from bibliography.models import Book,BookAuthorRelation,AuthorRole,Publication,Issue,IssueAuthorRelation

from . import booksearch

import json

class JsonCategoryNodesLinksView(View): 
    model = Category
    template_name = "bibliography/category_nodes_links.json"

    def get(self, request, *args, **kwargs):
        cat_maps={}
        root_maps={}

        roots=list(CategoryTreeNode.objects.roots())
        n=0
        max_num_objects=0
        for root in roots:
            root_maps[root.node_id]=n
            max_num_objects=max(max_num_objects,root.num_objects)
            n+=1


        if kwargs.has_key("pk"):
            parent=Category.objects.get(id=self.kwargs["pk"])
            min_level=parent.min_level()
            max_level=parent.my_branch_depth()
            cats=Category.objects.all_in_branch(self.kwargs["pk"])
            max_num_objects=parent.num_objects()
        else:
            min_level=0
            cats=Category.objects.all()
            max_level=CategoryTreeNode.objects.max_level()

        cats=list(cats)

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
            if not cat_maps.has_key(rel.parent.id): continue
            if not cat_maps.has_key(rel.child.id): continue
            source=cat_maps[rel.parent.id]
            target=cat_maps[rel.child.id]
            branch=rel.parent.my_branch_id()
            is_internal=(branch==rel.child.my_branch_id())
            rel_list.append( (source,target,root_maps[branch],is_internal,rel.parent.min_level()) )

        return render(request, self.template_name, 
                      {"category_list": category_list,
                       "rel_list": rel_list,
                       "num_branch": len(roots),
                       "max_num_objects": max_num_objects,
                       "min_level": min_level,
                       "max_level": max_level },
                      content_type='application/json')



class JsonCategoryNodesLinksView2(View): 
    model = Category
    template_name = "bibliography/category_nodes_links2.json"

    def get(self, request, *args, **kwargs):

        cat_maps={}
        root_maps={}

        roots=list(CategoryTreeNode.objects.roots())
        n=0
        max_num_objects=0
        for root in roots:
            root_maps[root.node_id]=n
            max_num_objects=max(max_num_objects,root.num_objects)
            n+=1


        if kwargs.has_key("pk"):
            parent=Category.objects.get(id=self.kwargs["pk"])
            min_level=parent.min_level()
            max_level=parent.my_branch_depth()
            cats=Category.objects.all_in_branch(self.kwargs["pk"])
            max_num_objects=parent.num_objects()
        else:
            min_level=0
            cats=Category.objects.all()
            max_level=CategoryTreeNode.objects.max_level()

        cats=list(cats)

        class Node(object):
            def __init__(self,category,group,branch,is_node_base,node_type="base",node_rel=None):
                self.category=category
                self.group=group
                self.branch=branch
                self.is_node_base=is_node_base
                self.node_type=node_type
                self.children=[]
                self.parents=[]
                self.index=0
                self.node_rel=node_rel
                self.posX=0
                self.posY=0
                self.side=0
                self.base_index=0

            def new_parent(self,parent):
                node=Node(self.category,self.group,self.branch,False,node_type="parent",node_rel=parent)
                link=Link(self,node,self.group,True,True)
                self.parents.append(node)
                return node,link

            def new_child(self,child):
                node=Node(self.category,self.group,self.branch,False,node_type="child",node_rel=child)
                link=Link(self,node,self.group,True,True)
                self.children.append(node)
                return node,link

            def name(self):
                name=self.category.name
                if not self.node_rel:
                    return name
                lab=self.node_type[0].upper()
                name+=" "+lab+":"+self.node_rel.category.name
                return name

            def calculate_positions(self):
                num_tot=len(self.parents)+len(self.children)
                sep=4
                positions=[]
                if num_tot==1:
                    positions=[ (0,sep) ]
                    self.side=2*sep
                elif num_tot==2:
                    positions=[ (0,sep),(0,-sep) ]
                    self.side=2*sep
                elif num_tot==3:
                    positions=[ (0,sep),(sep,0),(0,-sep) ]
                    self.side=2*sep
                elif num_tot==4:
                    positions=[ (0,sep),(sep,0),(0,-sep),(-sep,0) ]
                    self.side=2*sep
                else:
                    side_num=int(num_tot/4)+int(bool(num_tot%4))
                    self.side=side_num*sep+sep
                    y=self.side/2.0
                    for n in range(0,side_num):
                        x=-self.side/2.0+sep+n*sep
                        positions.append( (x,y) )
                    x=self.side/2.0
                    for n in range(0,side_num):
                        y=self.side/2.0-sep-n*sep
                        positions.append( (x,y) )
                    y=-self.side/2.0
                    for n in range(0,side_num):
                        x=self.side/2.0-sep-n*sep
                        positions.append( (x,y) )
                    x=-self.side/2.0
                    for n in range(0,side_num):
                        y=-self.side/2.0+sep+n*sep
                        positions.append( (x,y) )
                n=0
                for node in self.parents:
                    node.posX=positions[n][0]
                    node.posY=positions[n][1]
                    n+=1
                for node in self.children:
                    node.posX=positions[n][0]
                    node.posY=positions[n][1]
                    n+=1

        class Link(object):
            def __init__(self,parent_node,child_node,group,is_in_branch,is_internal):
                self.parent_node=parent_node
                self.child_node=child_node
                self.group=group
                self.is_in_branch=is_in_branch
                self.parent_level=self.parent_node.category.min_level()
                self.is_internal=is_internal
                self.num_objects=self.parent_node.category.num_objects()

        n=0
        base_nodes=[]
        base_nodes_by_catid={}
        for cat in cats:
            cat_maps[cat.id]=n
            branch=cat.my_branch_id()
            node=Node(cat,root_maps[branch],branch,True)
            base_nodes.append(node)
            base_nodes_by_catid[cat.id]=node
            n+=1

        cat_rel=CategoryRelation.objects.all()

        links=[]
        for rel in cat_rel:
            if not cat_maps.has_key(rel.parent.id): continue
            if not cat_maps.has_key(rel.child.id): continue
            source_base_node=base_nodes_by_catid[rel.parent.id]
            target_base_node=base_nodes_by_catid[rel.child.id]

            branch=rel.parent.my_branch_id()
            is_in_branch=(branch==rel.child.my_branch_id())
            source,s_link=source_base_node.new_child(target_base_node)
            target,t_link=target_base_node.new_parent(source_base_node)
            links.append(s_link)
            links.append(t_link)
            links.append( Link(source,target,root_maps[branch],is_in_branch,False) )

        nodes=[]
        n=0
        for bnode in base_nodes:
            bnode.index=n
            bnode.base_index=bnode.index
            bnode.calculate_positions()
            nodes.append(bnode)
            n+=1
            for node in bnode.parents:
                node.index=n
                node.base_index=bnode.index
                nodes.append(node)
                n+=1
            for node in bnode.children:
                node.index=n
                node.base_index=bnode.index
                nodes.append(node)
                n+=1

        return render(request, self.template_name, 
                      {"nodes": nodes,
                       "links": links,
                       "num_branch": len(roots),
                       "max_num_objects": max_num_objects,
                       "min_level": min_level,
                       "max_level": max_level },
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
        parent_id=self.kwargs["pk"]
        print parent_id
        return Category.objects.all_in_branch(parent_id)
        
        # parent=Category.objects.get(pk=parent_id)

        # children_ids=[]
        # for catnode in parent.tree_nodes.all():
        #     print catnode
        #     L=catnode.branch()
        #     for cn in L:
        #         print cn
        #     children_ids+=map(lambda x: x.object_id,list(L))
        # children_ids=list(set(children_ids))
        # print children_ids
        # print 100 in children_ids
        # return Category.objects.filter(id__in=children_ids)

class CategoryGraphView(TemplateView):
    template_name="bibliography/category_graph.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryGraphView, self).get_context_data(**kwargs)
        if kwargs.has_key("pk"):
            context["parent_id"]=kwargs["pk"]
        return context


class CategoryTreeView(TemplateView):
    template_name="bibliography/category_tree.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryTreeView, self).get_context_data(**kwargs)
        obj_list = list(CategoryTreeNode.objects.all())
        context["category_tree"]=map(lambda x: x.get_desc("catroot"),obj_list)
        return context


class CategorizerView(ListView):
    model = Category
    template_name = "bibliography/categorizer.html"

    def get_queryset(self, *args, **kwargs):
        qset=super(CategorizerView, self).get_queryset(*args, **kwargs)
        if not self.kwargs.has_key("pk"):
            return qset
        if not self.kwargs["pk"]:
            return qset
        parent_id=self.kwargs["pk"]
        print parent_id
        parent=Category.objects.get(pk=parent_id)

        children_ids=[]
        for catnode in parent.tree_nodes.all():
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
        formset = forms.CategorizerFormset(queryset=self.get_queryset())
        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = forms.CategorizerFormset(request.POST,request.FILES,queryset=self.get_queryset())
        if formset.is_valid():
            formset.save()
            formset = forms.CategorizerFormset(queryset=self.get_queryset())
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

class PublisherCreateView(CreateView):
    form_class=forms.PublisherForm
    model=Publisher
    template_name="bibliography/publisher_form.html"
    template_name_response="bibliography/publisher_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PublisherCreateView, self).get_context_data(**kwargs)
        context['address_formset'] = forms.PublisherAddressFormSet(prefix="address")
        return context

    def post(self, request, *args, **kwargs):
        form = forms.PublisherForm(request.POST)
        address_formset = forms.PublisherAddressFormSet(request.POST,prefix="address")

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
    form_class=forms.PublisherForm
    model=Publisher
    template_name="bibliography/publisher_form.html"
    template_name_response="bibliography/publisher_detail.json"

    def post(self, request, *args, **kwargs):
        form = forms.PublisherForm(request.POST)
        address_formset = forms.PublisherAddressFormSet(request.POST,prefix="address")

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

class AuthorCreateView(CreateView):
    form_class=forms.AuthorForm
    model=Author
    template_name="bibliography/author_form.html"
    template_name_response="bibliography/author_detail.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorCreateView, self).get_context_data(**kwargs)
        context['name_formset'] = forms.AuthorNameFormSet(prefix="name")
        return context

    def post(self, request, *args, **kwargs):
        form = forms.AuthorForm(request.POST)
        name_formset = forms.AuthorNameFormSet(request.POST,prefix="name")

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
                name_obj,created=PersonNameRelation.objects.get_or_create(person=author_obj,name_type=name_type,value=value)
        author_obj.update_cache()

        return author_obj

class JsonAuthorCreateView(AuthorCreateView):
    form_class=forms.AuthorForm
    model=Author
    template_name="bibliography/author_form.html"
    template_name_response="bibliography/author_detail.json"

    def post(self, request, *args, **kwargs):
        form = forms.AuthorForm(request.POST)
        name_formset = forms.AuthorNameFormSet(request.POST,prefix="name")

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

class BookCreateView(CreateView):
    form_class=forms.BookForm
    model=Book
    template_name="bibliography/book_form.html"
    template_name_response="bibliography/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super(BookCreateView, self).get_context_data(**kwargs)
        context['author_formset'] = forms.BookAuthorFormSet(prefix="author")
        return context

    def post(self, request, *args, **kwargs):
        form = forms.BookForm(request.POST)
        author_formset = forms.BookAuthorFormSet(request.POST,prefix="author")

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
    form_class=forms.BookForm
    model=Book
    template_name="bibliography/book_form.html"
    template_name_response="bibliography/book_detail.json"

    def post(self, request, *args, **kwargs):
        form = forms.BookForm(request.POST)
        author_formset = forms.BookAuthorFormSet(request.POST,prefix="author")

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

class JsonBookChangeCategoriesView(View):
    template_name_response="bibliography/book_detail.json"

    def post(self, request, *args, **kwargs):
        form = forms.CategoriesForm(request.POST)

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

class JsonCategoryChangeParentsView(View):
    template_name_response="bibliography/category_detail.json"

    def post(self, request, *args, **kwargs):
        form = forms.CategoriesForm(request.POST)

        data={}
        if not form.is_valid():
            data["form_errors"]=form.errors

        if data:
            data=json.dumps(data)
            return HttpResponse(data,status=400,content_type='application/json')

        child_id=self.kwargs['pk']
        child_obj=Category.objects.get(id=child_id)

        parents_txt=form.cleaned_data["categories"].strip()
        parents=map(lambda x: x.strip().replace('.','.*'),parents_txt.split(";"))
        parents_objects=[]

        for cat in parents:
            cat=cat.strip()
            if not cat: continue
            L=Category.objects.filter(name__iregex='^'+cat+'$')
            if len(L)==0:
                cat_obj=Category.objects.create(name=cat)
            else:
                cat_obj=L[0]
            parents_objects.append(cat_obj)

        print parents,parents_objects
        
        for rel_obj in child_obj.parent_set.all():
            print rel_obj
            if rel_obj.parent in parents_objects: continue
            print rel_obj
            rel_obj.delete()

        for cat_obj in parents_objects:
            CategoryRelation.objects.get_or_create(child=child_obj,parent=cat_obj)

        return render(request, self.template_name_response, 
                      {"category": child_obj},
                      content_type='application/json')




### Insert
class BooksInsertView(View): 
    template_name_isbn = "bibliography/isbn_form.html"
    template_name_insert = "bibliography/insert_tool.html"

    def get(self, request, *args, **kwargs):
        form = forms.IsbnForm()
        return render(request, self.template_name_isbn, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms.IsbnForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name_isbn, {'form': form})

        elenco=form.cleaned_data["elenco"].strip()

        isbn_list=[]
        for r in elenco.split("\n"):
            r=r.strip()
            t=r.split(" ")
            isbn_list+=t

        ## quello che viene ritornato, arrichito da quello che segue sotto
        params=booksearch.look_for(isbn_list)

        ## publisher da creare [ (str(n),pub.name,pubform,pubadrsformset) ]
        new_publisher_list=[]

        ## publisher che esistono già [pub]
        old_publisher_list=[]            

        n=0
        for pub in params["publisher_list"]:
            if pub.indb:
                old_publisher_list.append(pub)
                continue
            initial={ "isbn": pub.isbn_ced, "name": pub.name, "full_name": pub.name }
            pubform=forms.PublisherForm(prefix="newpublisher"+str(n),initial=initial)
            initial=[]
            if pub.addresses_indb:
                for adr in pub.addresses:
                    initial.append({"address":adr})
            else:
                for adr in pub.addresses:
                    initial.append({"city_name":adr})
            pubadrsformset=forms.PublisherAddressFormSet(prefix="newpublisher"+str(n)+"-address",initial=initial)
            new_publisher_list.append( (str(n),pub.name,pubform, pubadrsformset) )
            n+=1

        # book il cui publisher/author non esiste [ book ]
        suspended_book_list=[]

        # book da creare [ (str(n),book.isbn_10().replace("-","")+" "+book.title,bookform, bookauthorformset) ]
        new_book_list=[]

        # book che esistono già [ book ]
        old_book_list=[]

        # author da creare [ (str(n),aut,autform,autnamesformset) ]
        new_author_list=[]

        # author che esistono già [ aut ]
        old_author_list=[]

        temp_author_list=[]
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
            bookform=forms.BookForm(prefix="newbook"+str(n),initial=initial)
            initial=[]
            lauts=map(lambda x: (x[1],(x[0],x[2])),book.authors)
            lauts.sort()
            for pos,(role,author) in lauts:
                aut_role=AuthorRole.objects.get(label=role)
                initial.append({"author":author,"author_role":aut_role})
            bookauthorformset=forms.BookAuthorFormSet(prefix="newbook"+str(n)+"-author",initial=initial)
            new_book_list.append( (str(n),book.isbn_10().replace("-","")+u" "+unicode(book.title),bookform, bookauthorformset) )
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
            autform=forms.AuthorForm(prefix="newauthor"+str(n),initial={"format_collection":format_collection})
            autnamesformset=forms.AuthorNameFormSet(prefix="newauthor"+str(n)+"-name",initial=initial)
            new_author_list.append( (str(n),aut,autform,autnamesformset) )
            n+=1

        params["new_book_list"]=new_book_list
        params["suspended_book_list"]=suspended_book_list
        params["old_book_list"]=old_book_list
        params["new_author_list"]=new_author_list
        params["old_author_list"]=old_author_list
        params["new_publisher_list"]=new_publisher_list
        params["old_publisher_list"]=old_publisher_list

        return render(request, self.template_name_insert, params)

#### publication

class AuthorSearchView(View):
    template_name="bibliography/author_search.html"
    template_name_list="bibliography/author_list.html"
    template_name_not_found="bibliography/author_not_found.html"

    def get(self,request, *args,**kwargs):
        form = forms.SimpleSearchForm()
        return render(request, self.template_name, {'form': form})

    def render_not_found(self,request,form):
        return render(request,self.template_name_not_found,{"form": form})
        
    def post(self,request,*args,**kwargs):
        form = forms.SimpleSearchForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        search=form.cleaned_data["search"]
        L=list(Author.objects.filter_by_name(search))
        if not L:
            return self.render_not_found(request,form)
        if len(L)==1:
            print type(L[0])
            return redirect(L[0])
        return render(request,self.template_name_list,{"object_list":L})

class AuthorInsertView(AuthorSearchView):
    template_name_not_found="bibliography/author_form.html"

    def render_not_found(self,request,form):
        search=form.cleaned_data["search"]
        format_c,names=NameFormatCollection.objects.get_format_for_name(search)
        field_names=format_c.fields
        print format_c,field_names,names
        initial=[]
        for n in range(0,len(field_names)):
            name_type,created=NameType.objects.get_or_create(label=field_names[n])
            if len(names)>n:
                initial.append( {"value": names[n],"name_type": name_type.pk})
            else:
                initial.append( {"name_type": name_type.pk})
        print initial
        name_formset = forms.AuthorName0FormSet(prefix="name",initial=initial)
        author_form = forms.AuthorForm(initial={"format_collection": format_c})
        return render(request, self.template_name_not_found, 
                      {'form': author_form, 'name_formset': name_formset, 
                       "action": reverse("bibliography:author-create")})

class PublicationDetailView(DetailView): 
    model=Publication
    context_object_name="publication"

    def get_context_data(self, **kwargs):
        form = forms.SimpleSearchForm()
        context = super(PublicationDetailView, self).get_context_data(**kwargs)
        context["add_author_form"]=form
        return context

class PublicationIssuesAuthorChoiceView(View,SingleObjectMixin):
    template_name = "bibliography/publication_issues_author_choice.html"
    template_name_add = "bibliography/publication_issues_author_add.html"
    model=Publication
    context_object_name="publication"

    def get(self, request, *args, **kwargs):
        publication=self.get_object()
        form = forms.AuthorChoiceForm()
        return render(request, self.template_name, {self.context_object_name: publication,
                                                    'form': form})
        
    def post(self,request,*args,**kwargs):
        publication=self.get_object()
        print request.POST

        form = forms.AuthorChoiceForm(request.POST)

        if not form.is_valid():
            print "Invalid form"
            return render(request, self.template_name, {self.context_object_name: publication,'form': form})
        author=form.cleaned_data["author"]
        form = forms.IssueAuthorForm(prefix="author",initial={"author": author.pk})
        formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
        return render(request, self.template_name_add, {self.context_object_name: publication,
                                                        'author_form': form,
                                                        'issues_formset': formset,
                                                        'action': reverse("bibliography:publication-issues-author-add",
                                        kwargs={"pk":publication.id})})

class PublicationIssuesAuthorCreateView(View,SingleObjectMixin):
    template_name = "bibliography/author_form.html"
    template_name_add = "bibliography/publication_issues_author_add.html"
    model=Publication
    context_object_name="publication"

    def get(self, request, *args, **kwargs):
        publication=self.get_object()
        author_form = forms.AuthorForm()
        name_formset = forms.AuthorNameFormSet(request.POST,prefix="name")
        return render(request, self.template_name, 
                      {'form': author_form, 
                       'name_formset': name_formset, 
                       "action": reverse("bibliography:publication-issues-author-create",
                                        kwargs={"pk":publication.id})})
        
    def post(self, request, *args, **kwargs):
        publication=self.get_object()

        author_form = forms.AuthorForm(request.POST)
        name_formset = forms.AuthorNameFormSet(request.POST,prefix="name")

        if not author_form.is_valid():
            return render(request, self.template_name, 
                          {'form': author_form, 
                           'name_formset': name_formset, 
                           "action": reverse("bibliography:publication-issues-author-create",
                                        kwargs={"pk":publication.id})})

        if not name_formset.is_valid():
            return render(request, self.template_name, 
                          {'form': author_form, 
                           'name_formset': name_formset, 
                           "action": reverse("bibliography:publication-issues-author-create",
                                        kwargs={"pk":publication.id})})

        author=self.create_author(author_form,name_formset)
        form = forms.IssueAuthorForm(prefix="author",initial={"author": author.pk})
        formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
        return render(request, self.template_name_add, {self.context_object_name: publication,
                                                        'author_form': form,
                                                        'issues_formset': formset,
                                                        'action': reverse("bibliography:publication-issues-author-add",
                                        kwargs={"pk":publication.id})})
        
    def create_author(self,form,name_formset):
        format_collection=form.cleaned_data["format_collection"]
        author_obj=Author(format_collection=format_collection)
        author_obj.save()

        for row_data in name_formset.cleaned_data:
            if not row_data: continue
            name_type=row_data["name_type"]
            value=row_data["value"]
            if name_type:
                name_obj,created=PersonNameRelation.objects.get_or_create(person=author_obj,name_type=name_type,value=value)
        author_obj.update_cache()

        return author_obj


        

class PublicationIssuesAuthorSearchView(View,SingleObjectMixin):
    template_name = "bibliography/publication_issues_author_add.html"
    model=Publication
    context_object_name="publication"

    template_name_not_found="bibliography/author_form.html"
    template_name_multiple_found="bibliography/author_form_choice.html"
    template_name_choice = "bibliography/publication_issues_author_choice.html"
    template_name_create = "bibliography/author_form.html"

    ### questa pagina deve consentire di scegliere un autore tra object list e render
    ### qualcosa che poi si comporti così:
    # author=quello_scelto_dall_utente
    # publication=self.get_object()
    # form = forms.IssueAuthorForm(prefix="author",initial={"author": author.pk})
    # formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
    # return render(request, self.template_name, {self.context_object_name: publication,
    #                                             'author_form': form,
    #                                             'issues_formset': formset,
    #                                             'action': reverse("bibliography:publication-issues-author-add")})

    def render_multiple_found(self,request,object_list):
        publication=self.get_object()
        form = forms.AuthorChoiceForm()
        form.fields["author"].queryset=object_list
        return render(request, self.template_name_choice, 
                      {self.context_object_name: publication,
                       'form': form,
                       'action':reverse("bibliography:publication-issues-author-choice",
                                        kwargs={"pk":publication.id})})

        
    ### questa pagina deve consentire di creare un nuovo autore e render
    ### qualcosa che poi si comporti così:
    # author=quello_scelto_dall_utente
    # publication=self.get_object()
    # form = forms.IssueAuthorForm(prefix="author",initial={"author": author.pk})
    # formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
    # return render(request, self.template_name, {self.context_object_name: publication,
    #                                             'author_form': form,
    #                                             'issues_formset': formset,
    #                                             'action': reverse("bibliography:publication-issues-author-add")})

    def render_not_found(self,request,form):
        search=form.cleaned_data["search"]
        format_c,names=NameFormatCollection.objects.get_format_for_name(search)
        field_names=format_c.fields
        initial=[]
        for n in range(0,len(field_names)):
            name_type,created=NameType.objects.get_or_create(label=field_names[n])
            if len(names)>n:
                initial.append( {"value": names[n],"name_type": name_type.pk})
            else:
                initial.append( {"name_type": name_type.pk})
        name_formset = forms.AuthorName0FormSet(prefix="name",initial=initial)
        author_form = forms.AuthorForm(initial={"format_collection": format_c})
        publication=self.get_object()

        return render(request, self.template_name_create, 
                      {'form': author_form, 
                       'name_formset': name_formset, 
                       "action": reverse("bibliography:publication-issues-author-create",
                                        kwargs={"pk":publication.id})})

    def post(self,request,*args,**kwargs):
        form = forms.SimpleSearchForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        search=form.cleaned_data["search"]
        L=Author.objects.filter_by_name(search)
        if L.count()==0:
            return self.render_not_found(request,form)
        if L.count()>1:
            return self.render_multiple_found(request,L)

        author=L.first()
        publication=self.get_object()
        form = forms.IssueAuthorForm(prefix="author",initial={"author": author.pk})
        formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
        return render(request, self.template_name, {self.context_object_name: publication,
                                                    'author_form': form,
                                                    'issues_formset': formset,
                                                    'action': reverse("bibliography:publication-issues-author-add",
                                        kwargs={"pk":publication.id})})

class PublicationIssuesAuthorAddView(View,SingleObjectMixin):
    template_name = "bibliography/publication_issues_author_add.html"
    model=Publication
    context_object_name="publication"

    def get(self, request, *args, **kwargs):
        publication=self.get_object()
        form = forms.IssueAuthorForm(prefix="author")
        formset = forms.IssueChoiceFormset(prefix="issues",queryset=Issue.objects.by_publication(publication))
        return render(request, self.template_name, {self.context_object_name: publication,
                                                    'author_form': form,
                                                    'issues_formset': formset})

    def post(self, request, *args, **kwargs):
        publication=self.get_object()
        author_form = forms.IssueAuthorForm(request.POST,prefix="author")
        formset = forms.IssueChoiceFormset(request.POST,prefix="issues",
                                           queryset=Issue.objects.by_publication(publication))
        if not author_form.is_valid():
            return render(request, self.template_name, {self.context_object_name: publication,
                                                        'author_form': author_form,
                                                        'issues_formset': formset})
        if not formset.is_valid():
            return render(request, self.template_name, {self.context_object_name: publication,
                                                        'author_form': author_form,
                                                        'issues_formset': formset})
        # per ogni oggetto nella formset, bisogna creare una issueauthorrel con i valori passati

        author=author_form.cleaned_data["author"]
        author_role=author_form.cleaned_data["author_role"]
        author_pos=author_form.cleaned_data["pos"]

        for form in formset:
            if not form.cleaned_data["selected"]: continue
            obj,created=IssueAuthorRelation.objects.get_or_create(author=author,author_role=author_role,
                                                                  issue=form.instance,defaults={"pos": author_pos})
        # tornare alla publication
        return redirect(publication)


#### category graph

