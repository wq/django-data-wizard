from django.core.exceptions import ImproperlyConfigured
from collections import OrderedDict
from .settings import get_setting, import_from_string
from django.db import models


class Registry(object):
    _serializers = OrderedDict()
    _serializer_names = {}
    _loaders = {}
    _loader_classes = {}

    def get_class_name(self, serializer):
        return "%s.%s" % (serializer.__module__, serializer.__name__)

    def register(self, name, serializer=None):
        if isinstance(name, str):
            assert serializer
        elif isinstance(name, type) and issubclass(name, models.Model):
            model = name
            name = model._meta.verbose_name.title()
            if not serializer:
                serializer = self.create_serializer(model)
        else:
            raise Exception("Unexpected registration")

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
                "%s was already registered as %s" % (class_name, other_name)
            )

        self._serializers[name] = serializer
        self._serializer_names[class_name] = name

    def create_serializer(self, model):
        from natural_keys import NaturalKeyModelSerializer

        serializer = NaturalKeyModelSerializer.for_model(
            model,
            include_fields="__all__",
        )
        serializer.__qualname__ = serializer.__name__ = "{}Serializer".format(
            model.__name__
        )
        serializer.__module__ = "data_wizard.registry"
        return serializer

    def get_serializers(self):
        serializers = []
        for name, serializer in self._serializers.items():
            serializers.append(
                {
                    "name": name,
                    "serializer": serializer,
                    "class_name": self.get_class_name(serializer),
                    "options": self.get_serializer_options(name),
                }
            )
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

    def get_serializer_options(self, name):
        serializer = self.get_serializer(name)
        meta = getattr(serializer, "Meta", None)
        if not meta:
            return {}
        options = getattr(meta, "data_wizard", {})
        return options

    def get_choices(self):
        return [(s["class_name"], s["name"]) for s in self.get_serializers()]

    def set_loader(self, model, loader_name):
        self._loaders[model] = loader_name

    def get_loader_name(self, model):
        return self._loaders.get(model, get_setting("LOADER"))

    def get_loader(self, loader_name):
        reg = self._loader_classes
        if loader_name in reg:
            Loader = reg[loader_name]
        else:
            Loader = import_from_string(loader_name, "LOADER")
            reg[loader_name] = Loader
        return Loader


registry = Registry()
