from django.contrib import admin

from .models import *

admin.site.register(Variety)
admin.site.register(Pruning)
admin.site.register(Folding)
admin.site.register(Plot)
admin.site.register(PlotSection)
admin.site.register(Line)
admin.site.register(Season)
admin.site.register(RepairType)
admin.site.register(Repair)
admin.site.register(Task)
admin.site.register(PlotTask)
admin.site.register(LineState)
admin.site.register(Log)
admin.site.register(Reminder)