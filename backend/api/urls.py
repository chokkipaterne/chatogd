from django.urls import path, include
from django.conf.urls import url
from . import views

app_name = "api"

urlpatterns = [
    path('portals', views.portals, name="portals"),
    path('dataquality', views.dataquality, name="dataquality"),
    path('test', views.test, name="test"),
]
