from django.dispatch import Signal
import_complete = Signal(providing_args=['run', 'status'])
new_metadata = Signal(providing_args=['run', 'identifier'])
progress = Signal(providing_args=['run', 'status', 'meta'])
