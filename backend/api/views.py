from django.http import HttpResponse
from rest_framework import viewsets, status, generics
from django.conf import settings
from rest_framework.response import Response


from .models import *
from .serializers import *

class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer

class CepageViewSet(viewsets.ModelViewSet):
    queryset = Cepage.objects.all()
    serializer_class = CepageSerializer

class TailleViewSet(viewsets.ModelViewSet):
    queryset = Taille.objects.all()
    serializer_class = TailleSerializer

class PliageViewSet(viewsets.ModelViewSet):
    queryset = Pliage.objects.all()
    serializer_class = PliageSerializer

class RangViewSet(viewsets.ModelViewSet):
    queryset = Rang.objects.all()
    serializer_class = RangSerializer

    def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TacheViewSet(viewsets.ModelViewSet):
    queryset = Tache.objects.all()
    serializer_class = TacheSerializer

class LinesOfPlot(generics.ListAPIView):
    serializer_class = RangSerializer
    def get_queryset(self):
        parcelle_id = self.kwargs['parcelle_id']
        return Rang.objects.filter(parcelle=parcelle_id)

class SaisonViewSet(viewsets.ModelViewSet):
    queryset = Saison.objects.all().order_by("annee").reverse()
    serializer_class = SaisonSerializer

class TacheParcelleViewSet(viewsets.ModelViewSet):
    queryset = TacheParcelle.objects.all()
    serializer_class = TacheParcelleSerializer
    
class TasksOfPlotViewSet(viewsets.ModelViewSet):
    serializer_class = TacheParcelleSerializer
    def list(self, request, *args, **kwargs):
        parcelle_id = self.kwargs['parcelle_id']
        queryset = TacheParcelle.objects.filter(parcelle=parcelle_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
            parcelle_id = self.kwargs['parcelle_id']
            data = []
            for tache in request.data:
                data.append({ 'parcelle': parcelle_id, 'type_tache': tache })
            # Back up previous tasks for given plot
            queryset = TacheParcelle.objects.filter(parcelle=parcelle_id)
            previous_tasks = [ t.type_tache.id for t in queryset ]
            # Delete tasks of given plot
            queryset.delete()
            # Run validation
            serializer = self.get_serializer(data=data, many=True)
            try:
                serializer.is_valid(raise_exception=True)
            # If validation fails, restore backup tasks
            except ValidationError as exc:
                for task_id in previous_tasks:
                    task_plot = TacheParcelle(parcelle = parcelle_id, type_tache=task_id)
                    task_plot.save()
                raise ValidationError(exc)
            # Else, fill in the new tasks for the given plot
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

def Media(_, path):
    try:
        image_data = open(settings.MEDIA_ROOT + "/" + path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponse("Error: file not found...")