class BaseLoader(object):
    def __init__(self, run):
        self.run = run

    def load_io(self):
        raise NotImplementedError()


class FileLoader(BaseLoader):
    file_attr = 'file'

    @property
    def file(self):
        obj = self.run.content_object
        return getattr(obj, self.file_attr)

    def load_io(self):
        from wq.io import load_file
        options = self.load_file_options(self.run)
        return load_file(self.file.path, options=options)

    def load_file_options(self, run):
        headers = run.range_set.filter(type__in='head')
        if headers.exists():
            header_row = headers.first().start_row
            list_headers = run.range_set.filter(type__in='list')
            if list_headers.exists():
                start_row = list_headers.first().start_row
            else:
                start_row = header_row + 1
            return {
                'header_row': header_row,
                'start_row': start_row
            }

        if run.template:
            return self.load_file_options(run.template)

        return {}
