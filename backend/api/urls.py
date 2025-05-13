from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('parcelles', views.ParcelleViewSet)
router.register('cepages', views.CepageViewSet)
router.register('tailles', views.TailleViewSet)
router.register('pliages', views.PliageViewSet)
router.register('taches', views.TacheViewSet)
router.register('saisons', views.SaisonViewSet),
#router.register('taches_par_parcelle', views.TacheParcelleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('media/<path:path>/', views.Media),
    path('rangs/', views.RangViewSet.as_view({'get': 'list'})),
    path('parcelles/<int:parcelle_id>/rangs/', views.RangViewSet.as_view({'get': 'list_lines_of_plot', 'post': 'create'})),
    path('parcelles/<int:parcelle_id>/rangs/<int:saison_id>/', views.RangViewSet.as_view({'post': 'create'})),
    path('taches_par_parcelle/<int:parcelle_id>/', views.TasksOfPlotViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('taches_par_parcelle/<int:parcelle_id>/<int:saison_id>/', views.TasksOfPlotViewSet.as_view({'get': 'list', 'post': 'create'}))
]