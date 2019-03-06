from rest_framework import routers
from .views import RunViewSet


router = routers.SimpleRouter()
router.register(r'datawizard', RunViewSet)

app_name = 'data_wizard'
urlpatterns = router.urls
