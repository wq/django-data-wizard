from rest_framework import serializers
from wq.db import rest
from wq.db.rest.views import ModelViewSet
from wq.db.rest.serializers import ModelSerializer
from .models import Run
from data_wizard import views as wizard


# wq.db-compatible serializers
class CurrentUserDefault(serializers.CurrentUserDefault):
    def __call__(self):
        user = super(CurrentUserDefault, self).__call__()
        return user.pk


class RunSerializer(ModelSerializer, wizard.RunSerializer):
    user_id = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        exclude = ['content_type']


class RecordSerializer(wizard.RecordSerializer):
    object_url = serializers.SerializerMethodField()

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


# wq.db router registration
def user_filter(qs, request):
    if request.user.is_authenticated():
        return qs.filter(user=request.user)
    else:
        return qs.empty()


rest.router.register_model(
    Run,
    serializer=RunSerializer,
    viewset=RunViewSet,
    url='datawizard',
    modes=[],
    server_modes=[
        'detail', 'serializers', 'columns', 'ids', 'data', 'auto', 'records',
    ],
    fields="__all__",
    cache_filter=user_filter
)
