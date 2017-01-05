"""
Django settings for dynamic project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(BASE_DIR)

BASKERVILLE_HOME=BASE_DIR
BASKERVILLE_STYLE="original"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%%SECRET_KEY%%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'santaclara_base',
    'santaclara_editor',
    #'santaclara_css',
    'santaclara_third',
    "bibliography.apps.BibliographyConfig",
    'classification',
    #'foods'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dynamic.urls'

WSGI_APPLICATION = 'dynamic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'baskerville',      # Or path to database file if using sqlite3.
        'USER': 'baskerville',      # Not used with sqlite3.
        'PASSWORD': '%%DB_PASSWORD%%'
        'HOST': '',              # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',              # Set to empty string for default. Not used with sqlite3.

    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT= os.path.join( os.path.join(BASE_DIR, "web"), "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = BASKERVILLE_HOME+'/web/media/'

# STATICFILES_DIRS = (
#     # Put strings here, like "/home/html/static" or "C:/www/django/static".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     ("backgrounds", BASKERVILLE_HOME+"/static/backgrounds"),
#     ("brand", BASKERVILLE_HOME+"/static/brand"),
# )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/original')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "dynamic.template_vars.get_template_vars",
                "dynamic.template_vars_delegate.app_delegate",
            ],
        },
    },
]


# TEMPLATE_DIRS = (
#     # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     BASKERVILLE_HOME+"/templates/"+BASKERVILLE_STYLE,
# )

# TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
#                                "django.core.context_processors.debug",
#                                "django.core.context_processors.i18n",
#                                "django.core.context_processors.media",
#                                "django.core.context_processors.static",
#                                "django.core.context_processors.tz",
#                                "django.contrib.messages.context_processors.messages",
#                                "dynamic.template_vars.get_template_vars",
#                                "dynamic.template_vars_delegate.app_delegate",
#                                )

DELEGATED_TEMPLATE_CONTEXT_PROCESSORS = {
    'santaclara_css': (
        'santaclara_css.context_processors.variables',
        # 'santaclara_css.context_processors.colors',
        # 'santaclara_css.context_processors.shadows',
        )
    }


LOCALE_PATHS = (
    BASKERVILLE_HOME+'/locale',
)
