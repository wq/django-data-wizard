from rest_framework import routers
from django.core.exceptions import ImproperlyConfigured
from .views import RunViewSet
from . import discovered


if not discovered:
    raise ImproperlyConfigured(
        "data_wizard.urls imported before data_wizard.autodiscover(). "
        "Try moving data_wizard to an earlier position in INSTALLED_APPS."
    )


router = routers.SimpleRouter()
router.register(r"", RunViewSet)

app_name = "data_wizard"
urlpatterns = router.urls
