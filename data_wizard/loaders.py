class BaseLoader(object):
    def __init__(self, run):
        self.run = run

    def load_io_options(self):
        serializer = self.run.get_serializer()
        return getattr(serializer.Meta, 'data_wizard', {})


class FileLoader(BaseLoader):
    file_attr = 'file'

    @property
    def file(self):
        obj = self.run.content_object
        return getattr(obj, self.file_attr)

    def load_io(self):
        from wq.io import load_file
        options = self.load_io_options()
        return load_file(self.file.path, options=options)


class URLLoader(BaseLoader):
    url_attr = 'url'

    @property
    def url(self):
        obj = self.run.content_object
        return getattr(obj, self.url_attr)

    def load_io(self):
        from wq.io import load_url
        options = self.load_io_options()
        return load_url(self.url, options=options)
