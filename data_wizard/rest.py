from wq.db import rest
from .models import Run
from .serializers import RunSerializer
from .views import RunViewSet


rest.router.register_model(
    Run,
    serializer=RunSerializer,
    viewset=RunViewSet,
    url='datawizard',
)
