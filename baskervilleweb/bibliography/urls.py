from django.conf.urls import include, url
from django.conf import settings
from django.views.generic import DetailView,ListView,UpdateView,CreateView
from django.views.generic import TemplateView,ListView

from . import models,views

app_name="bibliography"

urlpatterns = [
    url( r'^$',TemplateView.as_view(template_name="bibliography/index.html"),name="index" ),
    url( r'^catalog/?$',views.CatalogView.as_view(),name="catalog"),
    url( r'^categories/?$',
         ListView.as_view(model=models.CategoryTreeNode,
                          queryset=models.CategoryTreeNode.objects.filter(level=0),
                          context_object_name="categorytreenode_list"),
         name="categories"),
    
    # url( r'^categories/graph/(?P<pk>\d+)/?$',views.CategoryGraphView.as_view()),
    # url( r'^categories/graph/?$',views.CategoryGraphView.as_view()),
    
    # url( r'^categories/graph2/(?P<pk>\d+)/?$',views.CategoryGraphView.as_view(template_name="bibliography/provad3.html")),
    # url( r'^categories/graph2/?$',views.CategoryGraphView.as_view(template_name="bibliography/provad3.html")),
    
    #url( r'^categories/graph/?$',ListView.as_view(model=CategoryTreeNode,
    #                                           template_name="bibliography/categorytreenode_graph.html",
    #                                           queryset=CategoryTreeNode.objects.filter(level=0),
    #                                           context_object_name="categorytreenode_list")),
    
    url( r'^categories/categorizer/(?P<pk>\d+)/?$',views.CategoryChildrenView.as_view(), name="categories-categorizer-branch"),
    
    url( r'^categories/categorizer/?$',views.CategoryChildrenView.as_view(),name="categories-categorizer"),
    url( r'^books/categorizer/',
         ListView.as_view(model=models.Book,
                          paginate_by=100,
                          context_object_name="book_list",
                          template_name="bibliography/book_categorizer.html"),
         name="books-categorizer"),
    
    url( r'^insert/',views.BooksInsertView.as_view(),name="insert"),
    url( r'^author/create/?$',views.AuthorCreateView.as_view(),name="author-create"),
    url( r'^author/search/?$',views.AuthorSearchView.as_view(),name="author-search"),
    url( r'^author/insert/?$',views.AuthorInsertView.as_view(),name="author-insert"),
    url( r'^author/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Author),name="author-detail"),
    url( r'^author/?$',ListView.as_view(
        model=models.Author,
        context_object_name="author_list",
        paginate_by=50),name="author-list"),
    url( r'^book/create/?$',views.BookCreateView.as_view(),name="book-create"),
    url( r'^book/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Book),name="book-detail"),

    url( r'^publisher/create/?$',views.PublisherCreateView.as_view(),name="publisher-create"),
    url( r'^publisher/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Publisher),name="publisher-detail"),
    url( r'^publisher/?$',ListView.as_view(model=models.Publisher),name="publisher-list"),

    url( r'^publisherisbn/?$',ListView.as_view(model=models.PublisherIsbn),name="publisherisbn-list"),
    url( r'^publisherisbn/alpha/?$',
         ListView.as_view(model=models.PublisherIsbn,queryset=models.PublisherIsbn.objects.isbn_alpha()),
         name="publisherisbn-alpha"),

    url( r'^books/seriewithoutisbn/?$',
         ListView.as_view(model=models.BookSerieWithoutIsbn),name="book-serie-without-isbn"),

    url( r'^books/alpha/?$',
         ListView.as_view(model=models.Book,queryset=models.Book.objects.isbn_alpha()),
         name="book-list-alpha"),
    url( r'^books/byisbnpub/(?P<isbn>.+?)/?$',
         views.BookByIsbnPubListView.as_view(),
         name="book-by-isbn-pub"),

    url( r'^publications/?$',
         ListView.as_view(model=models.Publication),
         name="publication-list"),
    url( r'^publications/alpha/?$',
         ListView.as_view(model=models.Publication,queryset=models.Publication.objects.issn_alpha()),
         name="publication-list-alpha"),
    url( r'^publication/(?P<pk>\d+)/?$',
         views.PublicationDetailView.as_view(),
         name="publication-detail"),
    url( r'^publication/(?P<pk>\d+)/add_author/?$',
         views.PublicationIssuesAuthorAddView.as_view(),
         name="publication-issues-author-add"),
    url( r'^publication/(?P<pk>\d+)/choice_author/?$',
         views.PublicationIssuesAuthorChoiceView.as_view(),
         name="publication-issues-author-choice"),
    url( r'^publication/(?P<pk>\d+)/create_author/?$',
         views.PublicationIssuesAuthorCreateView.as_view(),
         name="publication-issues-author-create"),
    url( r'^publication/(?P<pk>\d+)/search_author/?$',
         views.PublicationIssuesAuthorSearchView.as_view(),
         name="publication-issues-author-search"),

    url( r'^nameformatcollection/?$',
         ListView.as_view(model=models.NameFormatCollection),
         name="nameformatcollection-list"),

    # url( r'^json/categories/treenode/(?P<label_children>.+?)/(?P<level>\d+)/?$',views.JsonTreeView.as_view()),
    # url( r'^json/categories/nodeslinks/(?P<pk>\d+)/?$',views.JsonCategoryNodesLinksView.as_view()),
    # url( r'^json/categories/nodeslinks/?$',views.JsonCategoryNodesLinksView.as_view()),
    # url( r'^json/categories/nodeslinks2/(?P<pk>\d+)/?$',
    #   views.JsonCategoryNodesLinksView2.as_view()),
    # url( r'^json/categories/nodeslinks2/?$',
    #   views.JsonCategoryNodesLinksView2.as_view()),
    url( r'^json/publisher/create/?$',views.JsonPublisherCreateView.as_view(),name="json-publisher-create"),
    url( r'^json/publisher/(?P<pk>\d+)/?$',views.JsonDetailView.as_view(model=models.Publisher),name="json-publisher-detail"),
    url( r'^json/author/create/',views.JsonAuthorCreateView.as_view(),name="json-author-create"),
    url( r'^json/author/(?P<pk>\d+)/?$',views.JsonDetailView.as_view(model=models.Author),name="json-author-detail"),
    url( r'^json/book/create/?$',views.JsonBookCreateView.as_view(),name="json-book-create"),
    url( r'^json/book/(?P<pk>\d+)/?$',views.JsonDetailView.as_view(model=models.Book),name="json-book-detail"),
    url( r'^json/book/(?P<pk>\d+)/change_categories/?$',views.JsonBookChangeCategoriesView.as_view(),
         name="json-book-change-categories"),
    url( r'^json/category/(?P<pk>\d+)/change_parents/?$',views.JsonCategoryChangeParentsView.as_view(),
         name="json-category-change-parents"),
]

