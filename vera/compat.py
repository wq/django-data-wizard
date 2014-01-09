from django.db import models


def clone_field(field):
    """
    Incomplete backport of field.clone (coming in Django 1.7 and South 2)
    """
    if hasattr(field, 'clone'):
        return field.clone()

    cls = type(field)
    args = tuple()
    kwargs = {}

    if cls == models.ForeignKey:
        args = (field.rel.to,) + args

    kwargs['null'] = field.null
    kwargs['blank'] = field.blank
    if getattr(field, 'max_length', None):
        kwargs['max_length'] = field.max_length

    return cls(*args, **kwargs)
