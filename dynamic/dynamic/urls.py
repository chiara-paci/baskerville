from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from django.views.generic.base import TemplateView,RedirectView

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^/?$', RedirectView.as_view(url='/bibliography/catalog',permanent=False)),
                       )

urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
                        #url(r'^css/',         include('include-urls.urls-css')),
                        url(r'^css/',         include('santaclara_css.urls',app_name='santaclara_css')),
                        url(r'^bibliography/',include('bibliography.urls')),
                        )