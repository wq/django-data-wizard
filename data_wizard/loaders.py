class BaseLoader(object):
    default_serializer = None

    def __init__(self, run):
        self.run = run

    def get_serializer_name(self):
        return self.default_serializer

    @property
    def content_object(self):
        obj = self.run.content_object
        if not obj:
            raise Exception("Could not find {} with pk={}".format(
                self.run.content_type,
                self.run.object_id,
            ))
        return obj

    def load_io_options(self):
        serializer = self.run.get_serializer()
        return getattr(serializer.Meta, 'data_wizard', {})


class FileLoader(BaseLoader):
    file_attr = 'file'

    @property
    def file(self):
        return getattr(self.content_object, self.file_attr)

    def load_io(self):
        from wq.io import load_file
        options = self.load_io_options()
        return load_file(self.file.path, options=options)


class URLLoader(BaseLoader):
    url_attr = 'url'

    @property
    def url(self):
        return getattr(self.content_object, self.url_attr)

    def load_io(self):
        from wq.io import load_url
        options = self.load_io_options()
        return load_url(self.url, options=options)
