from django.http import HttpResponse
from rest_framework import viewsets, status, generics
from django.conf import settings
from rest_framework.response import Response


from .models import Parcelle, Cepage, Taille, Pliage, Rang
from .serializers import ParcelleSerializer, CepageSerializer, TailleSerializer, PliageSerializer, RangSerializer


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

class LinesOfPlot(generics.ListAPIView):
    serializer_class = RangSerializer
    def get_queryset(self):
        parcelle_id = self.kwargs['parcelle_id']
        return Rang.objects.filter(parcelle=parcelle_id)

def Media(_, path):
    try:
        image_data = open(settings.MEDIA_ROOT + "/" + path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponse("Error: file not found...")