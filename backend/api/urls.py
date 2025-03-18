from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('parcelles', views.ParcelleViewSet)
router.register('cepages', views.CepageViewSet)
router.register('tailles', views.TailleViewSet)
router.register('pliages', views.PliageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('media/<path:path>/', views.Media)
]