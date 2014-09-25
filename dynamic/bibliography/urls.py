from django.conf.urls import patterns, include, url
from django.conf import settings
#from django.views.generic import simple
from django.views.generic import DetailView,ListView,UpdateView,CreateView

#from bibliography.models import Page
#from santaclara_base.decorators import staff_or_404,permission_or_404

from django.views.generic import TemplateView,ListView

from bibliography.models import Author,CategoryTreeNode,Category,Publisher,Book
from bibliography.views import CategoryTreeView,JsonTreeView,CategorizerView,BooksInsertView,PublisherCreateView,JsonPublisherCreateView
from bibliography.views import AuthorCreateView,JsonAuthorCreateView,JsonCategoryChangeFathersView,CategoryChildrenView
from bibliography.views import BookCreateView,JsonBookCreateView,JsonBookChangeCategoriesView,JsonCategoryNodesLinksView

from santaclara_base.views import JsonDetailView

urlpatterns =patterns('',
                      ( r'^/?$',TemplateView.as_view(template_name="bibliography/index.html") ),
                      ( r'^catalog/?$',ListView.as_view(model=Author,
                                                        paginate_by=63,
                                                        context_object_name="author_list")),
                      ( r'^categories/?$',ListView.as_view(model=CategoryTreeNode,
                                                           queryset=CategoryTreeNode.objects.filter(level=0),
                                                           context_object_name="categorytreenode_list")),
                      ( r'^categories/graph/?$',ListView.as_view(model=CategoryTreeNode,
                                                                 template_name="bibliography/categorytreenode_graph.html",
                                                                 queryset=CategoryTreeNode.objects.filter(level=0),
                                                                 context_object_name="categorytreenode_list")),

                      ( r'^categories/categorizer/(?P<pk>\d+)/?$',CategoryChildrenView.as_view()),

                      ( r'^categories/categorizer/?$',CategoryChildrenView.as_view()),
                      ( r'^books/categorizer/',ListView.as_view(model=Book,
                                                                paginate_by=100,
                                                                context_object_name="book_list",
                                                                template_name="bibliography/book_categorizer.html")),

                      ( r'^insert/',BooksInsertView.as_view()),
                      ( r'^publisher/create/?$',PublisherCreateView.as_view()),
                      ( r'^publisher/(?P<pk>\d+)/?$',DetailView.as_view(model=Publisher)),
                      ( r'^author/create/?$',AuthorCreateView.as_view()),
                      ( r'^author/(?P<pk>\d+)/?$',DetailView.as_view(model=Author)),
                      ( r'^book/create/?$',BookCreateView.as_view()),
                      ( r'^book/(?P<pk>\d+)/?$',DetailView.as_view(model=Book)),
                      ( r'^categories/provad3/?$',TemplateView.as_view(template_name="bibliography/provad3.html") ),

                      ( r'^json/categories/treenode/(?P<label_children>.+?)/(?P<level>\d+)/?$',JsonTreeView.as_view()),
                      ( r'^json/categories/nodeslinks/?$',JsonCategoryNodesLinksView.as_view()),
                      ( r'^json/publisher/create/?$',JsonPublisherCreateView.as_view()),
                      ( r'^json/publisher/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Publisher)),
                      ( r'^json/author/create/',JsonAuthorCreateView.as_view()),
                      ( r'^json/author/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Author)),
                      ( r'^json/book/create/?$',JsonBookCreateView.as_view()),
                      ( r'^json/book/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Book)),
                      ( r'^json/book/(?P<pk>\d+)/change_categories/?$',JsonBookChangeCategoriesView.as_view()),
                      ( r'^json/category/(?P<pk>\d+)/change_fathers/?$',JsonCategoryChangeFathersView.as_view()),
                      )

