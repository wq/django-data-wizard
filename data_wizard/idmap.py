def never(value, field):
    return None


def existing(value, field):
    # FIXME: Move import to top when dropping Django 1.11
    from rest_framework.serializers import ValidationError
    try:
        field.to_internal_value(value)
    except ValidationError:
        return None
    else:
        return value


def always(value, field):
    return value
