"""
WSGI config for dynamic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

# import sys

# path = '/home/chiara/baskerville/baskervilleweb'
# if path not in sys.path:
#     sys.path.append(path)

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "baskervilleweb.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
