# FIXME: Drop this support in 2.0

try:
    from django.urls import reverse, NoReverseMatch
except ImportError:
    # Django 1.8
    from django.core.urlresolvers import reverse, NoReverseMatch

__all__ = ['reverse', 'NoReverseMatch']
