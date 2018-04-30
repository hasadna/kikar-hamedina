import os
import sys

import dj_database_url

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir))
REPOSITORY_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

sub_path = lambda *x: os.path.join(PROJECT_ROOT, *x)  # noqa: E731

# Configuring LOGS_ROOT
LOGS_ROOT = sub_path("logs")

# Configuring DATA_ROOT
DATA_ROOT = sub_path("data")

# Configuring MEDIA_ROOT
MEDIA_ROOT = sub_path("media")

# Configuring STATIC_ROOT
STATIC_ROOT = sub_path("collected_static")

# Configurion CLASSIFICATION_DATA_ROOT for autoTag and kikartags
CLASSIFICATION_DATA_ROOT = sub_path("classification_data")

# Additional locations of static files
STATICFILES_DIRS = (
    sub_path('static'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Configuring TEMPLATE_DIRS
        'DIRS': [
            sub_path("templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.request",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.core.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                # "planet.context_processors.context",
                "core.context_processors.generic",
                "zinnia.context_processors.version",
            ],
        },
    },
]

SECRET_KEY = (
    'yz2HiIDgrCDeHSfJSXIep3FeEQun!VhLXNCZ')  # override in local_settings.py

# Application definition

INSTALLED_APPS = (
    'modeltranslation',  # needs to be before admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.humanize',

    # Third-Party
    'django_comments',
    'rest_framework',
    'django_extensions',
    'pagination',
    'tagging',
    'dumpdata_chunks',
    'taggit',
    'tastypie',
    'mptt',
    'zinnia',
    'endless_pagination',
    # 'planet',
    'links',
    'video',
    'polymorphic',
    'corsheaders',
    'waffle',
    # Ours
    'kikartags',
    'knesset',
    'mks',
    'facebook_feeds',
    'core',
    'updater',
    'persons',
    'reporting',
    'polyorg',
    'actstream',  # Needs to be last
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'solid_i18n.middleware.SolidLocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'waffle.middleware.WaffleMiddleware',
)

ROOT_URLCONF = 'kikar_hamedina.urls'

WSGI_APPLICATION = 'kikar_hamedina.wsgi.application'

# schema://user:password@localhost:5432/db_name
config = dj_database_url.config(
    default='postgres://kikar:kikar@localhost:5432/kikar')
DATABASES = {'default': config}

# Default language, that will be used for requests without language prefix
LANGUAGE_CODE = 'he'

# supported languages
LANGUAGES = (
    ('he', 'Hebrew'),
    ('en', 'English'),
    ('ar', 'Arabic'),
)

# enable django translation
USE_I18N = True

# Optional. If you want to use redirects, set this to True
SOLID_I18N_USE_REDIRECTS = False

LOCALE_PATHS = (
    sub_path("locale"),
)
MODELTRANSLATION_DEBUG = False
MODELTRANSLATION_DEFAULT_LANGUAGE = 'he'

TIME_ZONE = 'Asia/Jerusalem'

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Django-planet settings
# PLANET = {
#     "USER_AGENT": "Kikar-Hamedina Planet/1.0"
# }

CORS_ORIGIN_WHITELIST = (
    'oknesset.org'
)

CORS_ALLOW_METHODS = (
    'GET',
    # 'POST',
    # 'PUT',
    # 'PATCH',
    # 'DELETE',
    # 'OPTIONS'
)
CORS_URLS_REGEX = r'^(/en/api.*)|(/ar/api.*)|/api.*$'

SITE_ID = 1

LANGUAGE_COOKIE_NAME = "he"
SESSION_COOKIE_NAME = "myplanetid"

CURRENT_KNESSET_NUMBER = 20
CURRENT_ELECTED_KNESSET_NUMBER = CURRENT_KNESSET_NUMBER + 1

IS_ELECTIONS_MODE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(asctime)s %(module)s %(process)d '
                '%(thread)d %(message)s')
        },
        'simple': {
            'format': '%(levelname)s - %(asctime)s - %(message)s'
        },
    },
    'handlers': {
        'scrapeFile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '%s/debug.log' % os.path.join(REPOSITORY_ROOT, 'log'),
            'formatter': 'simple'
        },
        'scraping': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '%s/scarping.log' % os.path.join(REPOSITORY_ROOT,
                                                         'log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB each log file
            'backupCount': 10,
            'formatter': 'simple'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'scraping': {
            'handlers': ['scraping'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

TASTYPIE_DEFAULT_FORMATS = ['json']

NUMBER_OF_TRIES_FOR_REQUEST = 2

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

if TESTING:
    class DisableMigrations(object):
        '''
            this is a workaround for an issue with django==1.8
            where the migrations that run before tests are too slow.
            This workaround skips migrations in tests
            see https://code.djangoproject.com/ticket/23745
        '''

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "nomigrations"

    MIGRATION_MODULES = DisableMigrations()

if "TRAVIS" in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'travisci',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    DEBUG = True

    FACEBOOK_APP_ID = '1090127617700980'
    FACEBOOK_SECRET_KEY = 'fd9b75e36b581192447e8eca1ade8ee3'
    FACEBOOK_API_VERSION = 'v2.7'

    TESTING = False

try:
    from .local_settings import *  # noqa
except ImportError:
    pass
