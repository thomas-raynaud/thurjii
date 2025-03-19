from .models import Parcelle, Cepage, Taille, Pliage
from rest_framework import serializers
import json

class ParcelleSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField()
    cepage = serializers.PrimaryKeyRelatedField(queryset=Cepage.objects.all())
    taille = serializers.PrimaryKeyRelatedField(queryset=Taille.objects.all())
    pliage = serializers.PrimaryKeyRelatedField(queryset=Pliage.objects.all())
    """
    taille_img_x = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    taille_img_y = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        return obj.image.name"""
    
    def get_region(self, obj):
        region = json.loads(obj.region.json)['coordinates'][0]
        out_region = [ { 'x': p[0], 'y': p[1] } for p in region ]
        return out_region

    class Meta:
        model = Parcelle
        fields = [ 'id', 'nom', 'region', 'cepage', 'taille', 'pliage' ]


class CepageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cepage
        fields = [ 'id', 'nom' ]


class TailleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taille
        fields = [ 'id', 'nom' ]


class PliageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pliage
        fields = [ 'id', 'nom' ]