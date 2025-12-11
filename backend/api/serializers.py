from .models import *
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
import pyproj
from shapely.geometry import Polygon

class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = [ 'id', 'name', 'designation', 'variety', 'pruning', 'folding' ]

class PlotSectionSerializer(GeoFeatureModelSerializer):
    area = serializers.SerializerMethodField()
    def get_area(self, obj):
        transformer = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
        coords = [ transformer.transform(point[0], point[1]) for point in obj.region[0] ]
        geod = pyproj.Geod(ellps="WGS84")
        poly = Polygon(coords)
        return abs(geod.geometry_area_perimeter(poly)[0])
    class Meta:
        model = PlotSection
        geo_field = "region"
        fields = [ 'id', 'name', 'area', 'plot' ]

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = [ 'id', 'name', 'color' ]

class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = [ 'id', 'name', 'color' ]


class PruningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pruning
        fields = [ 'id', 'name', 'color' ]


class FoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folding
        fields = [ 'id', 'name', 'color' ]

class LineSerializer(GeoFeatureModelSerializer):
    plot = serializers.SerializerMethodField()
    class Meta:
        model = Line
        geo_field = "location"
        fields = [ 'id', 'plot', 'plot_section' ]
    def get_plot(self, obj):
        return obj.plot_section.plot.id

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
        return obj.task.name

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
    def get_line_position(self, obj):
        return [ { 'x': p[0], 'y': p[1] } for p in obj.line.location ]
    
    class Meta:
        model = LineState
        fields = [ 'line', 'plot_task', 'plot', 'task', 'season', 'done', 'get_line_position' ]

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