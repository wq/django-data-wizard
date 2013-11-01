from wq.db.rest import app
from wq.db.patterns.base import swapper

from .models import Result
Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')

from .serializers import ResultSerializer, EventSerializer, ReportSerializer

if not Result._meta.abstract:
    app.router.register_model(Result, serializer=ResultSerializer)
app.router.register_model(Event, serializer=EventSerializer)
app.router.register_model(Report, serializer=ReportSerializer)
