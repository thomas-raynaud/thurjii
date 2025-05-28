from .models import *
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
import pyproj
from shapely.geometry import Polygon

class PlotSerializer(GeoFeatureModelSerializer):
    area = serializers.SerializerMethodField()
    def get_area(self, obj):
        transformer = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
        coords = [ transformer.transform(point[0], point[1]) for point in obj.region[0] ]
        geod = pyproj.Geod(ellps="WGS84")
        poly = Polygon(coords)
        return abs(geod.geometry_area_perimeter(poly)[0])
    class Meta:
        model = Plot
        geo_field = "region"
        fields = [ 'id', 'name', 'variety', 'pruning', 'folding', 'area' ]

class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = [ 'id', 'name' ]


class PruningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pruning
        fields = [ 'id', 'name' ]


class FoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folding
        fields = [ 'id', 'name' ]

class LineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Line
        geo_field = "location"
        fields = [ 'id', 'plot' ]

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [ 'id', 'name' ]

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [ 'year', 'start', 'end' ]

class PlotTaskSerializer(serializers.ModelSerializer):
    task_name = serializers.SerializerMethodField()
    def get_task_name(self, obj):
        return Task.objects.get(pk=obj.task.id).name

    class Meta:
        model = PlotTask
        fields = [ 'id', 'plot', 'task', 'task_name', 'season' ]

class LineStateSerializer(serializers.ModelSerializer):
    plot = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()
    line_location = serializers.SerializerMethodField()
    def get_plot(self, obj):
        return obj.plot_task.plot.id
    def get_task(self, obj):
        return obj.plot_task.task.id
    def get_season(self, obj):
        return obj.plot_task.season.year
    def get_line_location(self, obj):
        return {
            'start': [ obj.line.location[0][0], obj.line.location[0][1] ],
            'end': [ obj.line.location[1][0], obj.line.location[1][1] ]
        }
    
    class Meta:
        model = LineState
        fields = [ 'line', 'plot_task', 'plot', 'task', 'season', 'done', 'line_location' ]

class LogSerializer(serializers.ModelSerializer):
    plot_name = serializers.SerializerMethodField()
    task_name = serializers.SerializerMethodField()
    def get_plot_name(self, obj):
        return obj.plot_task.plot.name
    def get_task_name(self, obj):
        return obj.plot_task.task.name
    class Meta:
        model = Log
        fields = [ 'id', 'plot_task', 'plot_name', 'task_name', 'nb_hours', 'date', 'comment' ]