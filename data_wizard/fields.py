from rest_framework import serializers
from django.utils.six import string_types
import datetime


DATE_FIELDS = {
    'DateTimeField': datetime.datetime,
    'DateField': datetime.date,
}


class DateTimeSplitField(serializers.Field):
    # FIXME
    pass


def process_date_FIXME(meta_field, meta_datatype, meta_key, val, obj):
    # A meta_field value of '[field].[part]' indicates a value is split across
    # multiple columns.  For example, a spreadsheet could contain two columns
    # (date and time) that would be merged into a single "observed" field on a
    # custom Event class.  There would then be two MetaColumns values, with
    # names of "observed.date" and "observed.time" respectively.
    if '.' in meta_field:
        meta_field, part = meta_field.split('.')
    else:
        part = None

    # Automatically parse date values as such
    if (meta_datatype in DATE_FIELDS and isinstance(val, string_types) and
            part != 'time'):
        from dateutil.parser import parse
        val = parse(val)
        if meta_datatype == 'DateField':
            val = val.date()

    # If field is already set by an earlier column, this value might be the
    # second half of a date/time pair.
    if obj[meta_key].get(meta_field, None) is not None:
        if not part:
            raise Exception(
                'Multiple columns found for %s' % meta_field
            )
        if part not in ('date', 'time'):
            raise Exception(
                'Unexpected multi-column field name: %s.%s!' % (
                    meta_field, part
                )
            )
        other_val = obj[meta_key][meta_field]
        val = process_date_part(val, other_val, part)


def process_date_part(new_val, old_val, part):
    """
    Combine separate date & time columns into a single value.
    """

    if part == 'date':
        date, time = new_val, old_val
    else:
        date, time = old_val, new_val

    # Date should already be a valid date (see parse in save_metadata_value)
    if not isinstance(date, datetime.date):
        raise Exception("Expected date but got %s!" % date)

    # Try some extra hacks to convert time values
    if not isinstance(time, datetime.time):
        if (isinstance(time, float) and
                time >= 100 and time <= 2400):
            # "Numeric" time (hour * 100 + minutes)
            time = str(time)
        elif isinstance(time, string_types) and ":" in time:
            # Take out semicolon for isdigit() code below
            time = time.replace(":", "")

        # FIXME: what about seconds?
        if time.isdigit() and len(time) in (3, 4):
            if len(time) == 3:
                # 300 -> time(3, 0)
                time = datetime.time(
                    int(time[0]),
                    int(time[1:])
                )
            else:
                # 1200 -> time(12, 0)
                time = datetime.time(
                    int(time[0:2]),
                    int(time[2:])
                )
        else:
            # Meh, it was worth a shot
            raise Exception("Expected time but got %s!" % time)
    return datetime.datetime.combine(date, time)
