from django.dispatch import Signal
import_complete = Signal(providing_args=['instance', 'status'])
new_metadata = Signal(providing_args=['instance', 'object', 'identifier'])
