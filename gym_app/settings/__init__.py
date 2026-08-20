"""Settings package: select the active settings module via DJANGO_SETTINGS_ENV.

Usage:
  DJANGO_SETTINGS_ENV=development -> loads gym_app.settings.development
  DJANGO_SETTINGS_ENV=production  -> loads gym_app.settings.production
  DJANGO_SETTINGS_ENV=test        -> loads gym_app.settings.test

`DJANGO_SETTINGS_MODULE=gym_app.settings` resolves to this __init__, which
re-exports the chosen submodule's attributes into the package namespace so
Django sees a flat settings module.
"""
import importlib
import os

_env = os.environ.get('DJANGO_SETTINGS_ENV', 'development').lower()

_module = importlib.import_module(f'.{_env}', package=__name__)
globals().update(vars(_module))
