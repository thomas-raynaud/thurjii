from rest_framework import viewsets, status
from django.conf import settings
from rest_framework.response import Response

from .models import *
from .serializers import *

class PlotViewSet(viewsets.ModelViewSet):
    queryset = Plot.objects.all().order_by('id')
    serializer_class = PlotSerializer
    def list(self, request, *args, **kwargs):
        plot_data = self.get_serializer(self.queryset, many=True).data
        for i in range(0, len(plot_data)):
            plot_sections = PlotSection.objects.filter(plot=plot_data[i]['id'])
            plot_data[i]['plot_sections'] = PlotSectionSerializer(plot_sections, many=True).data
        return Response(plot_data)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        plot_data = self.get_serializer(instance).data
        plot_sections = PlotSection.objects.filter(plot=plot_data['id'])
        plot_data['plot_sections'] = PlotSectionSerializer(plot_sections, many=True).data
        return Response(plot_data)

class VarietyViewSet(viewsets.ModelViewSet):
    queryset = Variety.objects.all()
    serializer_class = VarietySerializer

class PruningViewSet(viewsets.ModelViewSet):
    queryset = Pruning.objects.all()
    serializer_class = PruningSerializer

class FoldingViewSet(viewsets.ModelViewSet):
    queryset = Folding.objects.all()
    serializer_class = FoldingSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer

    def list_plot_lines(self, request, *args, **kwargs):
        plot_id = self.kwargs['plot_id']
        queryset = Line.objects.filter(plot=plot_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        plot_id = self.kwargs['plot_id']
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Add LineStates if the plot has tasks attached to it
        try:
            year = self.kwargs['year']
        except KeyError:
            year = Season.objects.all().order_by("year").reverse().first().year
        plot_tasks = PlotTask.objects.filter(plot=plot_id, season=year)
        plot_lines = Line.objects.filter(plot=plot_id)
        for line in plot_lines:
            for task in plot_tasks:
                line_state = LineState(
                    line=line,
                    plot_task=task,
                    done=False
                )
                line_state.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data['features'], status=status.HTTP_201_CREATED, headers=headers)

class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all().order_by("year").reverse()
    serializer_class = SeasonSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_season = serializer.save()
        # Create the PlotTasks and LineStates for this new season, based on the previous season's PlotTasks
        if self.queryset.count() > 0:
            previous_season = self.queryset[0]
            plots = Plot.objects.all()
            for plot in plots:
                plot_tasks_previous_season = PlotTask.objects.filter(plot=plot, season=previous_season)
                for plot_task_previous_season in plot_tasks_previous_season:
                    # Create PlotTasks for the new season
                    new_plot_task = PlotTask(plot=plot, season=new_season, task=plot_task_previous_season.task)
                    new_plot_task.save()
                    # Create LineStates for the new season
                    plot_lines = Line.objects.filter(plot=plot)
                    for line in plot_lines:
                        line_state = LineState(
                            line=line,
                            plot_task=new_plot_task,
                            done=False
                        )
                        line_state.save()
        return Response(None, status=status.HTTP_201_CREATED)
    
class PlotTaskViewSet(viewsets.ModelViewSet):
    queryset = PlotTask.objects.all()
    serializer_class = PlotTaskSerializer

    def list_plot_season_plot_tasks(self, request, *args, **kwargs):
        plot_id = self.kwargs['plot_id']
        year = self.kwargs['year']
        queryset = PlotTask.objects.filter(plot=plot_id, season=year)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        plot_id = self.kwargs['plot_id']
        try:
            year = self.kwargs['year']
        except KeyError:
            year = Season.objects.all().order_by("year").reverse().first().year
        tasks_request = request.data
        plot_tasks = PlotTask.objects.filter(plot=plot_id, season=year)
        previous_tasks = [ t.task.id for t in plot_tasks ]
        plot_lines = Line.objects.filter(plot=plot_id)
        plot = Plot.objects.get(pk = plot_id)
        season = Season.objects.get(pk = year)
        # If some tasks are not already registered to the plot, add the new PlotTasks and the new LineStates
        for task_request in tasks_request:
            if task_request not in previous_tasks:
                # Register the new task to the plot
                task = Task.objects.get(pk = task_request)
                plot_task = PlotTask(
                    plot=plot,
                    task=task,
                    season=season
                )
                plot_task.save()
                # Add Line for each line in the plot
                for line in plot_lines:
                    line_state = LineState(
                        line=line,
                        plot_task=plot_task,
                        done=False
                    )
                    line_state.save()
        # If some previous tasks are not in the new list of task, delete them
        for previous_task in previous_tasks:
            if previous_task not in tasks_request:
                # Delete the plot task
                task = Task.objects.get(pk = previous_task)
                plot_task = PlotTask.objects.get(
                    plot=plot,
                    task=previous_task,
                    season=season
                )
                plot_task.delete()
        new_plot_tasks = PlotTask.objects.filter(plot=plot_id, season=year)
        serializer = self.get_serializer(new_plot_tasks, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all().order_by("date", "id").reverse()
    serializer_class = LogSerializer

    def list_season_logs(self, request, *args, **kwargs):
        year = self.kwargs['year']
        plot_tasks_season = PlotTask.objects.filter(season=year)
        serializer = self.get_serializer(self.queryset.filter(plot_task__in=plot_tasks_season), many=True)
        return Response(serializer.data)

class LineStateViewSet(viewsets.ModelViewSet):
    serializer_class = LineStateSerializer

    def list(self, request, *args, **kwargs):
        plot_id = self.kwargs['plot_id']
        year = self.kwargs['year']
        plot_tasks_season = PlotTask.objects.filter(plot=plot_id, season=year)
        queryset = LineState.objects.all().filter(plot_task__in=plot_tasks_season)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update_line_states(self, request, *args, **kwargs):
        new_line_states = request.data
        for new_line_state in new_line_states:
            line_state = LineState.objects.filter(line=new_line_state['line'], plot_task=new_line_state['plot_task'])[0]
            line_state.done = new_line_state['done']
            line_state.save()
        return Response(None, status=status.HTTP_200_OK)