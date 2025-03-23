from .models import Parcelle, Cepage, Taille, Pliage, Rang
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class ParcelleSerializer(GeoFeatureModelSerializer):
    """
    taille_img_x = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    taille_img_y = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        return obj.image.name"""
    class Meta:
        model = Parcelle
        geo_field = "region"
        fields = [ 'id', 'nom', 'cepage', 'taille', 'pliage' ]


class RangSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Rang
        geo_field = "location"
        fields = [ 'id', 'parcelle' ]


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