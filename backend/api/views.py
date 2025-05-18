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

    def list_lines_of_plot(self, request, *args, **kwargs):
        parcelle_id = self.kwargs['parcelle_id']
        queryset = Rang.objects.filter(parcelle=parcelle_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        parcelle_id = self.kwargs['parcelle_id']
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Add EtatRang if the plot has tasks attached to it
        try:
            saison = self.kwargs['saison_id']
        except KeyError:
            saison = Saison.objects.all().order_by("annee").reverse().first().annee
        parcelle_db = Parcelle.objects.get(id=parcelle_id)
        saison_db = Saison.objects.get(annee=saison)
        taches_parcelle_db = TacheParcelle.objects.filter(parcelle=parcelle_db, saison=saison_db)
        rangs_parcelle_db = Rang.objects.filter(parcelle=parcelle_db)
        for rang_db in rangs_parcelle_db:
            for tache in taches_parcelle_db:
                etat_rang = EtatRang(
                    rang=rang_db,
                    tache_parcelle=tache,
                    fait=False
                )
                etat_rang.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data['features'], status=status.HTTP_201_CREATED, headers=headers)

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
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_season_db = serializer.save()
        # Créer les TacheParcelles et EtatRangs pour cette année en se basant sur la dernière saison
        last_season_db = self.queryset[0]
        if self.queryset.count() > 0:
            parcelles_db = Parcelle.objects.all()
            for parcelle_db in parcelles_db:
                taches_parcelle_db = TacheParcelle.objects.filter(parcelle=parcelle_db, saison=last_season_db)
                for tache_parcelle_db in taches_parcelle_db:
                    new_tache_parcelle_db = TacheParcelle(parcelle=parcelle_db, saison=new_season_db, type_tache=tache_parcelle_db.type_tache)
                    new_tache_parcelle_db.save()
                    rangs_parcelle_db = Rang.objects.filter(parcelle=parcelle_db)
                    for rang_db in rangs_parcelle_db:
                        etat_rang = EtatRang(
                            rang=rang_db,
                            tache_parcelle=new_tache_parcelle_db,
                            fait=False
                        )
                        etat_rang.save()
        return Response(None, status=status.HTTP_201_CREATED)

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
        try:
            saison = self.kwargs['saison_id']
        except KeyError:
            saison = Saison.objects.all().order_by("annee").reverse().first().annee
        tasks = request.data
        saison_db = Saison.objects.get(annee=saison)
        taches_parcelle_db = TacheParcelle.objects.filter(parcelle=parcelle_id, saison=saison_db)
        previous_tasks = [ t.type_tache.id for t in taches_parcelle_db ]
        parcelle_db = Parcelle.objects.get(id=parcelle_id)
        rangs_parcelle_db = Rang.objects.filter(parcelle=parcelle_db)
        for task in tasks:
            if task not in previous_tasks:
                # Add the new task for the plot
                tache_db = Tache.objects.get(id=task)
                task_plot = TacheParcelle(
                    parcelle=parcelle_db,
                    type_tache=tache_db,
                    saison=saison_db
                )
                task_plot.save()
                # Add EtatRang for each line in the plot
                for rang in rangs_parcelle_db:
                    etat_rang = EtatRang(
                        rang=rang,
                        tache_parcelle=task_plot,
                        fait=False
                    )
                    etat_rang.save()
        for prev_task in previous_tasks:
            tache_db = Tache.objects.get(id=prev_task)
            if prev_task not in tasks:
                # Delete the task for the plot
                task_plot = TacheParcelle.objects.get(
                    parcelle=parcelle_db,
                    type_tache=tache_db,
                    saison=saison_db
                )
                task_plot.delete()
        return Response(None, status=status.HTTP_201_CREATED)

def Media(_, path):
    try:
        image_data = open(settings.MEDIA_ROOT + "/" + path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponse("Error: file not found...")