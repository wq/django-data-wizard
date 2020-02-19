from rest_framework.serializers import ValidationError


def never(value, field):
    return None


def existing(value, field):
    try:
        field.to_internal_value(value)
    except ValidationError:
        return None
    else:
        return value


def always(value, field):
    return value
