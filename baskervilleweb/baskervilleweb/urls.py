from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic.base import TemplateView,RedirectView
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.utils.text import capfirst
from django.urls import NoReverseMatch, reverse, path
from django.apps import apps
import six
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _, ugettext_lazy

from . import admin as myadmin

#admin.site=myadmin.MyAdminSite(admin.site)
#admin.sites.site=admin.site

urlpatterns = [
#    path(r'admin/doc/', include('django.contrib.admindocs.urls')),
#    path(r'admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

import baskervilleauth.urls
import recipebook.urls
import bibliography.urls
import foods.urls
import archive.urls

urlpatterns += [
    path(r'',TemplateView.as_view(template_name="home/index.html"),name="home" ),
    path(r'tools/',TemplateView.as_view(template_name="home/tools.html"),name="tools" ),
    path(r'accounts/', include(baskervilleauth.urls)),
    path(r'recipebook/',include(recipebook.urls)),
    path(r'foods/',include(foods.urls)),
    path(r'bibliography/',include(bibliography.urls)),
    path(r'archive/',include(archive.urls)),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

