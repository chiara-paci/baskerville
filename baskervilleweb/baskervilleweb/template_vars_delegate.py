from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module

def app_delegate(request):
    """
    Leverage the DELEGATED_TEMPLATE_CONTEXT_PROCESSORS setting and url
    application namespaces to delegate template context processors to
    individual apps.
    
    E.g.
    # settings.py
    TEMPLATE_CONTEXT_PROCESSORS = (
        # ...
        'path.to.app_delegate'
    )
    
    DELEGATED_TEMPLATE_CONTEXT_PROCESSORS = {
        'myapp': (
            'myproject.myapp.context_processors.do_something',
        )
    }
    
    # urls.py
    (r'^myapp', include('myproject.myapp.urls', app_name='myapp'))
    
    # The above will execute the "do_something" template context processor for
    # views accessed via urls in the "myapp" application namespace.
    """
    
    app_name = resolve(request.path).app_name

    print resolve(request.path)
    print request.path
    
    try:
        processors = settings.DELEGATED_TEMPLATE_CONTEXT_PROCESSORS[app_name]
    except KeyError:
        # Not delegating any processors to this app
        return {}
    except AttributeError:
        raise ImproperlyConfigured('DELEGATED_TEMPLATE_CONTEXT_PROCESSORS setting required to use app delegation of template context processors')
    
    context = {}
    
    # Adapted from django.template.context.get_standard_processors
    for path in processors:
        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]

        print "x",i,module,attr
        
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
        
        try:
            func = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
        
        context.update(func(request))
    
    return context
