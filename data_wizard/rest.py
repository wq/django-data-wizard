from wq.db import rest
from .models import Run
from .views import RunViewSet


rest.router.register_model(
    Run,
    viewset=RunViewSet,
    url='datawizard',
)
