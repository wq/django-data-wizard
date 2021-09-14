from rest_framework import serializers
from wq.db import rest
from wq.db.rest.views import ModelViewSet
from wq.db.rest.serializers import ModelSerializer
from wq.db.rest.renderers import HTMLRenderer, JSONRenderer
from .models import Run
from . import views as wizard
from rest_framework.settings import api_settings


# wq.db-compatible serializers
class CurrentUserDefault(serializers.CurrentUserDefault):
    def __call__(self, serializer=None):
        if getattr(self, 'requires_context', None):
            # DRF 3.11+
            user = super(CurrentUserDefault, self).__call__(serializer)
        else:
            # DRF 3.10 and earlier
            user = super(CurrentUserDefault, self).__call__()
        return user.pk


class RunSerializer(ModelSerializer, wizard.RunSerializer):
    user_id = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        exclude = ['content_type']


class RecordSerializer(wizard.RecordSerializer):
    def get_object_url(self, instance):
        obj = instance.content_object
        conf = rest.router.get_model_config(type(obj))
        if not conf:
            return None

        urlbase = conf['url']
        objid = getattr(obj, conf.get('lookup', 'pk'))
        return "%s/%s" % (urlbase, objid)


class RunViewSet(ModelViewSet, wizard.RunViewSet):
    record_serializer_class = RecordSerializer
    renderer_classes = [HTMLRenderer, JSONRenderer]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    _namespace = 'wq'


# wq.db router registration
def user_filter(qs, request):
    if request.user.is_authenticated:
        return qs.filter(user=request.user)
    else:
        return qs.none()


rest.router.register_model(
    Run,
    serializer=RunSerializer,
    viewset=RunViewSet,
    url='datawizard',
    modes=[
        'list', 'detail', 'edit',
        'serializers', 'columns', 'ids', 'data', 'auto', 'records',
    ],
    postsave='datawizard/{{id}}{{#task_id}}/auto?task={{task_id}}{{/task_id}}',
    fields="__all__",
    filter=user_filter,
    cache='none',
)
