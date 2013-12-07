from django.dispatch import Signal
import_complete = Signal(providing_args=['file', 'status'])
