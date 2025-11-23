from django.db import models
from datetime import date
from django.contrib.gis.db import models as modelsPG

class Variety(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=6, default="")
    def __str__(self):
        return self.name

class Pruning(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=6, default="")
    def __str__(self):
        return self.name

class Folding(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=6, default="")
    def __str__(self):
        return self.name

class Designation(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=6, default="")
    def __str__(self):
        return self.name

class Plot(models.Model):
    name = models.CharField(max_length=50, unique=True)
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    pruning = models.ForeignKey(Pruning, on_delete=models.CASCADE)
    folding = models.ForeignKey(Folding, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class PlotSection(models.Model):
    name = models.CharField(max_length=50)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    region = modelsPG.PolygonField()
    def __str__(self):
        return self.name + "(" + self.plot.name + ")"

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.IntegerField(unique=True)

class PlotGroup(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class Line(models.Model):
    plot_section = models.ForeignKey(PlotSection, on_delete=models.CASCADE)
    location = modelsPG.LineStringField()
    def __str__(self):
        return "Line " + str(self.id) + " of plot " + self.plot_section.plot.name + " (" + self.plot_section.name + ")"

class Season(models.Model):
    year = models.IntegerField(unique=True, primary_key=True)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    def __str__(self):
        return "Season " + str(self.year)

class RepairType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Repair(models.Model):
    repair_type = models.ForeignKey(RepairType, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    position = models.DecimalField(max_digits=3, decimal_places=3)
    accident_date = models.DateField(default=date.today)
    repaired = models.BooleanField(default=False)
    def __str__(self):
        return  (
            "Repair of " + str(self.line) + " - type : " + str(self.repair_type)
            + (" (repaired)" if self.realisee else "")
            + " - date : " + self.accident_date
        )

class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class PlotTask(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[ 'plot', 'task', 'season' ],
                name='unique_plot_task_season_combination'
            )
        ]
    def __str__(self):
        return str(self.plot) + " - " + str(self.task) + " - " + str(self.season)

class LineState(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    plot_task = models.ForeignKey(PlotTask, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[ 'line', 'plot_task' ],
                name='unique_line_plot_task_combination'
            )
        ]
    def __str__(self):
        return str(self.line) + " - " + str(self.plot_task) + (" (done)" if self.done else "")

class Log(models.Model):
    plot_task = models.ForeignKey(PlotTask, on_delete=models.CASCADE)
    nb_hours = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    comment = models.TextField(max_length=300, blank=True)
    def __str__(self):
        return (
            "Log of plot " + self.plot_task.plot.name + " - "
            + str(self.plot_task.task) + " - " + str(self.date)
        )

class Reminder(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    done = models.BooleanField(default=0)
    def __str__(self):
        return (
            self.name + " - " + self.date + (" (done)" if self.done else "")
        )