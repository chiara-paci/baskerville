from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic.base import TemplateView,RedirectView
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.utils.text import capfirst
from django.core.urlresolvers import NoReverseMatch, reverse
from django.apps import apps
from django.utils import six
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _, ugettext_lazy

from bibliography.models import custom_model_list as bibliography_custom_model_list

class MyAdminSite(admin.AdminSite):
    site_header="Baskerville Admin"
    site_title="Baskerville Admin"
    app_with_custom_model_list={ "bibliography": bibliography_custom_model_list }

    def __init__(self,old_site):
        admin.AdminSite.__init__(self)
        self._registry=old_site._registry
        self._actions = old_site._actions
        self._global_actions = old_site._global_actions

    def each_context(self,request):
        context=super(MyAdminSite,self).each_context(request)
        context["app_index_block_template_default"]="admin/app_index_block.html"
        context["app_with_custom_block_template"]=self.app_with_custom_model_list.keys()
        return context

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = model_admin.has_module_permission(request)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                        'model_label':  model._meta.model_name.lower()
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': apps.get_app_config(app_label).verbose_name,
                            'app_label': app_label,
                            'app_url': reverse(
                                'admin:app_list',
                                kwargs={'app_label': app_label},
                                current_app=self.name,
                            ),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            if self.app_with_custom_model_list.has_key(app["app_label"]):
                app["custom_models"]=self.app_with_custom_model_list[app["app_label"]](app['models'])

        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
        )
        context.update(extra_context or {})

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or
                                'admin/index.html', context)

    def app_index(self, request, app_label, extra_context=None):
        app_name = apps.get_app_config(app_label).verbose_name
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                has_module_perms = model_admin.has_module_permission(request)
                if not has_module_perms:
                    raise PermissionDenied

                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                        'model_label':  model._meta.model_name.lower()
                    }
                    if perms.get('change'):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_dict:
                        app_dict['models'].append(model_dict),
                    else:
                        # First time around, now that we know there's
                        # something to display, add in the necessary meta
                        # information.
                        app_dict = {
                            'name': app_name,
                            'app_label': app_label,
                            'app_url': '',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        if self.app_with_custom_model_list.has_key(app_dict["app_label"]):
            app_dict["custom_models"]=self.app_with_custom_model_list[app_dict["app_label"]](app_dict['models'])
        app_dict['models'].sort(key=lambda x: x['name'])
        context = dict(self.each_context(request),
            title=_('%(app)s administration') % {'app': app_name},
            app_list=[app_dict],
            app_label=app_label,
        )
        context.update(extra_context or {})

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context)

admin.site=MyAdminSite(admin.site)
admin.sites.site=admin.site

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(url='/bibliography/catalog',permanent=False),name="home"),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    url(r'^bibliography/',include('bibliography.urls')),
]
