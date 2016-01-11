from wq.db import rest
from wq.db.patterns.serializers import IdentifiedModelSerializer
from .models import Site

rest.router.register_serializer(Site, IdentifiedModelSerializer)
