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
            raise Exception(
                "Could not find {} with pk={}".format(
                    self.run.content_type,
                    self.run.object_id,
                )
            )
        return obj

    def load_iter_options(self):
        return {
            key: val
            for key, val in self.run.get_serializer_options().items()
            if key in self.valid_options
        }


class FileLoader(BaseLoader):
    file_attr = "file"
    valid_options = {"header_row", "start_row"}

    @property
    def file(self):
        file = getattr(self.content_object, self.file_attr)
        return file.file

    def load_iter(self):
        from itertable import load_file

        options = self.load_iter_options()
        return load_file(self.file, options=options)


class URLLoader(BaseLoader):
    url_attr = "url"
    valid_options = {"header_row", "start_row"}

    @property
    def url(self):
        return getattr(self.content_object, self.url_attr)

    def load_iter(self):
        from itertable import load_url

        options = self.load_iter_options()
        return load_url(self.url, options=options)
