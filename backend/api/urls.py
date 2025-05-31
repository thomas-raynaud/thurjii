from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('plots', views.PlotViewSet)
router.register('varieties', views.VarietyViewSet)
router.register('prunings', views.PruningViewSet)
router.register('foldings', views.FoldingViewSet)
router.register('tasks', views.TaskViewSet)
router.register('seasons', views.SeasonViewSet),
router.register('logs', views.LogViewSet),
router.register('plot_tasks', views.PlotTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lines/', views.LineViewSet.as_view({ 'get': 'list' })),
    path('plots/<int:plot_id>/lines/', views.LineViewSet.as_view({ 'get': 'list_plot_lines', 'post': 'create' })),
    path('plots/<int:plot_id>/lines/<int:year>/', views.LineViewSet.as_view({ 'post': 'create' })),
    path('plots/<int:plot_id>/lines/<int:year>/state/', views.LineStateViewSet.as_view({ 'get': 'list' })),
    path('line_states/', views.LineStateViewSet.as_view({ 'put': 'update_line_states' })),
    path('plots/<int:plot_id>/plot_tasks/<int:year>/', views.PlotTaskViewSet.as_view({ 'get': 'list_plot_season_plot_tasks', 'post': 'create' })),
    path('logs/season/<int:year>/', views.LogViewSet.as_view({'get': 'list_season_logs'}))
]