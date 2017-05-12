from rest_framework import routers
from .views import RunViewSet


router = routers.SimpleRouter()
router.register(r'datawizard', RunViewSet)


urlpatterns = router.urls
