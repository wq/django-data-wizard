from .models import IoModel
from django.conf import settings

import swapper
File = swapper.load_model('files', 'File')


class FileIoProxy(File, IoModel):
    """
    Proxy model to add IoModel functionality to files.File or whatever File is
    swapped out for.  Defined here instead of in models.py to avoid module
    ordering issues with swapper.load_model()
    """

    def load_io(self, **options):
        from wq.io import load_file
        filename = "%s/%s" % (settings.MEDIA_ROOT, self.file.name)
        if not options:
            options = self.load_file_options()
        return load_file(filename, options=options)

    def load_file_options(self):
        headers = self.relationships.filter(
            type__name='Contains Column',
            range__type='list'
        )
        if headers.exists():
            header_row = headers[0].range_set.get(type='head').start_row
            start_row = headers[0].range_set.get(type='list').start_row
            return {
                'header_row': header_row,
                'start_row': start_row
            }

        templates = self.inverserelationships.filter(
            type__inverse_name='Template'
        )
        if templates.exists():
            template = templates[0].right
            # Template is probably missing the proxy functionality
            template = FileIoProxy.objects.get(pk=template.pk)
            return template.load_file_options()
        return {}

    class Meta:
        proxy = True
