from django.core.exceptions import ImproperlyConfigured
from collections import OrderedDict


class Registry(object):
    _registry = OrderedDict()
    _serializer_names = {}

    def get_class_name(self, serializer):
        return "%s.%s" % (serializer.__module__, serializer.__name__)

    def register(self, name, serializer):
        class_name = self.get_class_name(serializer)
        if name in self._registry:
            other_class = self.get_class_name(self._registry[name])
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

        self._registry[name] = serializer
        self._serializer_names[class_name] = name

    def get_serializers(self):
        serializers = []
        for name, serializer in self._registry.items():
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
        if name not in self._registry:
            raise ImproperlyConfigured(
                "%s is not a registered serializer!" % name
            )
        return self._registry[name]

    def get_choices(self):
        return [
            (s['class_name'], s['name'])
            for s in self.get_serializers()
        ]


registry = Registry()
