from wq.db.rest import app
from wq.db.patterns.base import swapper
from .serializers import EventSerializer, ReportSerializer, ResultSerializer

Event = swapper.load_model('vera', 'Event')
Report = swapper.load_model('vera', 'Report')
Result = swapper.load_model('vera', 'Result')

app.router.register_model(Event, serializer=EventSerializer)
app.router.register_model(Report, serializer=ReportSerializer)
app.router.register_model(Result, serializer=ResultSerializer)
