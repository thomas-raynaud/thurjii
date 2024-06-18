from django.http import HttpResponse
from rest_framework import viewsets
from django.conf import settings

from .models import Parcelle
from .serializers import ParcelleSerializer


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer

def Media(_, path):
    try:
        image_data = open(settings.MEDIA_ROOT + "/" + path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponse("Error: file not found...")