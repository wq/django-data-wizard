from django.core.exceptions import ImproperlyConfigured
from collections import OrderedDict
from rest_framework.settings import import_from_string
from django.conf import settings


class Registry(object):
    _serializers = OrderedDict()
    _serializer_names = {}
    _loaders = {}
    _loader_classes = {}

    def get_class_name(self, serializer):
        return "%s.%s" % (serializer.__module__, serializer.__name__)

    def register(self, name, serializer):
        class_name = self.get_class_name(serializer)
        if name in self._serializers:
            other_class = self.get_class_name(self._serializers[name])
            raise ImproperlyConfigured(
                "Could not register serializer %s: "
                "the name '%s' was already registered for %s"
                % (self.get_class_name(serializer), name, other_class)
            )

        if class_name in self._serializer_names:
            other_name = self._serializer_names[class_name]
            raise ImproperlyConfigured(
                "%s was already registered as %s"
                % (class_name, other_name)
            )

        Meta = getattr(serializer, 'Meta', None)
        if not Meta or not hasattr(Meta, 'model'):
            raise ImproperlyConfigured(
                "%s.Meta is missing a model!" % class_name
            )

        self._serializers[name] = serializer
        self._serializer_names[class_name] = name

    def get_serializers(self):
        serializers = []
        for name, serializer in self._serializers.items():
            serializers.append({
                'name': name,
                'serializer': serializer,
                'class_name': self.get_class_name(serializer),
            })
        return serializers

    def get_serializer_name(self, name):
        return self._serializer_names.get(name, name)

    def get_serializer(self, name):
        name = self.get_serializer_name(name)
        if name not in self._serializers:
            raise ImproperlyConfigured(
                "%s is not a registered serializer!" % name
            )
        return self._serializers[name]

    def get_choices(self):
        return [
            (s['class_name'], s['name'])
            for s in self.get_serializers()
        ]

    def set_loader(self, model, loader_name):
        self._loaders[model] = loader_name

    def get_loader_name(self, model):
        default_loader = getattr(
            settings, 'DATA_WIZARD_LOADER', 'data_wizard.loaders.FileLoader'
        )
        return self._loaders.get(model, default_loader)

    def get_loader(self, loader_name):
        reg = self._loader_classes
        if loader_name in reg:
            Loader = reg[loader_name]
        else:
            Loader = import_from_string(loader_name, 'DATA_WIZARD_LOADER')
            reg[loader_name] = Loader
        return Loader


registry = Registry()
