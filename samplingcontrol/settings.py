"""
Django settings for samplingcontrol project on Heroku. Fore more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import os
import dj_database_url
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "v5)389x0%so^it+fi0-!y#r1ty-zl(c=x&u-bc9s5jv(fvh8d)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
USE_TZ = True

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks', 
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'import_export',
    'admininterface',
    #'apiv1',
    'apiv2',
    'feedback'

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'admininterface.middleware.CheckRole'
)

ROOT_URLCONF = 'samplingcontrol.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'samplingcontrol.wsgi.application'

# LOGIN URLS
LOGIN_URL='/login/'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Sampling user model
AUTH_USER_MODEL = 'admininterface.User'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()

# Enable Persistent Connections
DATABASES['default']['CONN_MAX_AGE'] = 500

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')
MEDIA_URL  = '/media/'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Rest framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}


# Configure Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s | %(name)s@%(lineno)d | %(message)s ',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'filters': ['require_debug_false'],
#            'class': 'django.utils.log.AdminEmailHandler'
#        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
#        'production_file': {
#            'level': 'INFO',
#            'class': 'logging.handlers.RotatingFileHandler',
#            'filename': 'logs/main.log',
#            'maxBytes': 1024 * 1024 * 5,  # 5 MB
#            'backupCount': 7,
#            'formatter': 'main_formatter',
#            'filters': ['require_debug_false'],
#        },
#        'debug_file': {
#            'level': 'DEBUG',
#            'class': 'logging.handlers.RotatingFileHandler',
#            'filename': 'logs/main_debug.log',
#            'maxBytes': 1024 * 1024 * 5,  # 5 MB
#            'backupCount': 7,
#            'formatter': 'main_formatter',
#            'filters': ['require_debug_true'],
#        },
        'null': {
            "class": 'logging.NullHandler',            
        }
    },
    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins', 'console'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#        'django': {
#            'handlers': ['console', ],
#        },
#        'py.warnings': {
#            'handlers': ['console', ],
#        },
#        '': {
#            'handlers': ['console', 'production_file', 'debug_file'],
#            'level': "INFO",
#        },
        '': {
            'handlers': ['console'],
            'level': "INFO",
        },
    }
}

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# The behaviour though shall be the same.
# For instance we can define in localsettings.py the following line:
# 
# INSTALLED_APPS += (
#    'debug_toolbar.apps.DebugToolbarConfig',  # Enabling django-debug-toolbar
# )
# Otherwise, using `from .local_settings import *` forces us to rewrite the
# entire variable in localsettings, making it harder to maintain.

f = os.path.join(PROJECT_PATH, "localsettings.py")
if os.path.exists(f):
    exec(open(f, "rb").read())