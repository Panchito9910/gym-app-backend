"""Test settings.

Uses SQLite in-memory database for fast test runs without requiring SQL Server.
"""
from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = ()  # noqa: F405
