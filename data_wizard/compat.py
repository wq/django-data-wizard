# FIXME: Drop this support in 2.0

try:
    from django.urls import reverse, NoReverseMatch
except ImportError:
    # Django 1.8
    from django.core.urlresolvers import reverse, NoReverseMatch

try:
    from rest_framework.decorators import action
except ImportError:
    # DRF 3.6
    from rest_framework.decorators import detail_route

    def action(detail=True, methods=None):
        return detail_route(methods)


__all__ = ['reverse', 'NoReverseMatch', 'action']
