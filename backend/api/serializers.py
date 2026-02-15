from .models import *
from .libs.geometry import *
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


def get_sum_distance_plot_lines(plot):
    plot_sections = PlotSection.objects.filter(plot=plot.id)
    lines = Line.objects.filter(plot_section__in=plot_sections)
    sum_distances = 0.0
    for line in lines:
        sum_distances += get_distance(line.location)
    return sum_distances

def get_sum_distance_plot_lines_done(plot_task):
    plot_sections = PlotSection.objects.filter(plot=plot_task.plot.id)
    lines = Line.objects.filter(plot_section__in=plot_sections)
    line_states = LineState.objects.filter(line__in=lines)
    sum_distances_lines_done = 0.0
    for line, line_state in zip(lines, line_states):
        if line_state.done:
            sum_distances_lines_done += get_distance(line.location)
    return sum_distances_lines_done


class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = [ 'id', 'name', 'designation', 'variety', 'pruning', 'folding' ]

class PlotSectionSerializer(GeoFeatureModelSerializer):
    area = serializers.SerializerMethodField()
    def get_area(self, obj):
        return get_area_polygon(obj.region[0])
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
    completion = serializers.SerializerMethodField()
    def get_completion(self, obj):
        plot_tasks = PlotTask.objects.filter(task=obj.id)
        if len(plot_tasks) == 0:
            return -1.0
        sum_lines_distance = 0.0
        sum_lines_done_distance = 0.0
        for plot_task in plot_tasks:
            sum_lines_distance += get_sum_distance_plot_lines(plot_task.plot)
            sum_lines_done_distance += get_sum_distance_plot_lines_done(plot_task)
        return sum_lines_done_distance / sum_lines_distance
    class Meta:
        model = Task
        fields = [ 'id', 'name', 'completion' ]

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [ 'year', 'start', 'end' ]

class PlotTaskSerializer(serializers.ModelSerializer):
    task_name = serializers.SerializerMethodField()
    completion = serializers.SerializerMethodField()
    def get_task_name(self, obj):
        return obj.task.name
    def get_completion(self, obj):
        sum_dist = get_sum_distance_plot_lines(obj.plot)
        if sum_dist == 0.0:
            return 0.0
        return get_sum_distance_plot_lines_done(obj) / sum_dist

    class Meta:
        model = PlotTask
        fields = [ 'id', 'plot', 'task', 'task_name', 'season', 'completion' ]

class LineStateSerializer(serializers.ModelSerializer):
    plot = serializers.SerializerMethodField()
    plot_section = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()
    line_location = serializers.SerializerMethodField()
    def get_plot(self, obj):
        return obj.plot_task.plot.id
    def get_plot_section(self, obj):
        return obj.line.plot_section.id
    def get_task(self, obj):
        return obj.plot_task.task.id
    def get_season(self, obj):
        return obj.plot_task.season.year
    def get_line_location(self, obj):
        return [ { 'x': p[0], 'y': p[1] } for p in obj.line.location ]
    
    class Meta:
        model = LineState
        fields = [ 'line', 'plot_task', 'plot', 'plot_section', 'task', 'season', 'done', 'line_location' ]

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