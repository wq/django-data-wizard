from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('data_wizard.urls')),
]
