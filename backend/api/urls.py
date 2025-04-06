from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('parcelles', views.ParcelleViewSet)
router.register('cepages', views.CepageViewSet)
router.register('tailles', views.TailleViewSet)
router.register('pliages', views.PliageViewSet)
router.register('rangs', views.RangViewSet)
router.register('taches', views.TacheViewSet)
router.register('saisons', views.SaisonViewSet),
router.register('taches_par_parcelles', views.TacheParcelleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('media/<path:path>/', views.Media),
    path('parcelles/<int:parcelle_id>/rangs/', views.LinesOfPlot.as_view()),
    path('taches_par_parcelles/<int:parcelle_id>/', views.TasksOfPlot.as_view())
]