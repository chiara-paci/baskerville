from django.conf.urls import include, url
from django.conf import settings
#from django.views.generic import simple
from django.views.generic import DetailView,ListView,UpdateView,CreateView

#from bibliography.models import Page
#from santaclara_base.decorators import staff_or_404,permission_or_404

from django.views.generic import TemplateView,ListView

from bibliography.models import Author,Person,CategoryTreeNode,Category,Publisher,Book
from bibliography.views import CategoryTreeView,JsonTreeView,CategorizerView,BooksInsertView,PublisherCreateView,JsonPublisherCreateView
from bibliography.views import AuthorCreateView,JsonAuthorCreateView,JsonCategoryChangeParentsView,CategoryChildrenView,CategoryGraphView
from bibliography.views import BookCreateView,JsonBookCreateView,JsonBookChangeCategoriesView,JsonCategoryNodesLinksView,JsonCategoryNodesLinksView2

from santaclara_base.views import JsonDetailView

urlpatterns = [
    url( r'^$',TemplateView.as_view(template_name="bibliography/index.html") ),
    url( r'^catalog/?$',ListView.as_view(model=Author,
                                      paginate_by=63,
                                      context_object_name="author_list")),
    url( r'^categories/?$',ListView.as_view(model=CategoryTreeNode,
                                         queryset=CategoryTreeNode.objects.filter(level=0),
                                         context_object_name="categorytreenode_list")),
    
    url( r'^categories/graph/(?P<pk>\d+)/?$',CategoryGraphView.as_view()),
    url( r'^categories/graph/?$',CategoryGraphView.as_view()),
    
    url( r'^categories/graph2/(?P<pk>\d+)/?$',CategoryGraphView.as_view(template_name="bibliography/provad3.html")),
    url( r'^categories/graph2/?$',CategoryGraphView.as_view(template_name="bibliography/provad3.html")),
    
    #url( r'^categories/graph/?$',ListView.as_view(model=CategoryTreeNode,
    #                                           template_name="bibliography/categorytreenode_graph.html",
    #                                           queryset=CategoryTreeNode.objects.filter(level=0),
    #                                           context_object_name="categorytreenode_list")),
    
    url( r'^categories/categorizer/(?P<pk>\d+)/?$',CategoryChildrenView.as_view()),
    
    url( r'^categories/categorizer/?$',CategoryChildrenView.as_view()),
    url( r'^books/categorizer/',ListView.as_view(model=Book,
                                              paginate_by=100,
                                              context_object_name="book_list",
                                              template_name="bibliography/book_categorizer.html")),
    
    url( r'^insert/',BooksInsertView.as_view()),
    url( r'^publisher/create/?$',PublisherCreateView.as_view()),
    url( r'^publisher/(?P<pk>\d+)/?$',DetailView.as_view(model=Publisher)),
    url( r'^author/create/?$',AuthorCreateView.as_view()),
    url( r'^author/(?P<pk>\d+)/?$',DetailView.as_view(model=Author)),
    url( r'^book/create/?$',BookCreateView.as_view()),
    url( r'^book/(?P<pk>\d+)/?$',DetailView.as_view(model=Book)),
    url( r'^json/categories/treenode/(?P<label_children>.+?)/(?P<level>\d+)/?$',JsonTreeView.as_view()),
    url( r'^json/categories/nodeslinks/(?P<pk>\d+)/?$',JsonCategoryNodesLinksView.as_view()),
    url( r'^json/categories/nodeslinks/?$',JsonCategoryNodesLinksView.as_view()),
    url( r'^json/categories/nodeslinks2/(?P<pk>\d+)/?$',
      JsonCategoryNodesLinksView2.as_view()),
    url( r'^json/categories/nodeslinks2/?$',
      JsonCategoryNodesLinksView2.as_view()),
    url( r'^json/publisher/create/?$',JsonPublisherCreateView.as_view()),
    url( r'^json/publisher/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Publisher)),
    url( r'^json/author/create/',JsonAuthorCreateView.as_view()),
    url( r'^json/author/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Author)),
    url( r'^json/book/create/?$',JsonBookCreateView.as_view()),
    url( r'^json/book/(?P<pk>\d+)/?$',JsonDetailView.as_view(model=Book)),
    url( r'^json/book/(?P<pk>\d+)/change_categories/?$',JsonBookChangeCategoriesView.as_view()),
    url( r'^json/category/(?P<pk>\d+)/change_parents/?$',JsonCategoryChangeParentsView.as_view()),
]

