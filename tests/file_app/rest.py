from wq.db.rest import app
from dbio.views import IoViewSet
from .models import File

app.router.register_model(File, viewset=IoViewSet)
