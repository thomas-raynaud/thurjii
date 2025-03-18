from django.http import HttpResponse
from rest_framework import viewsets
from django.conf import settings

from .models import Parcelle, Cepage, Taille, Pliage
from .serializers import ParcelleSerializer, CepageSerializer, TailleSerializer, PliageSerializer


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

def Media(_, path):
    try:
        image_data = open(settings.MEDIA_ROOT + "/" + path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponse("Error: file not found...")