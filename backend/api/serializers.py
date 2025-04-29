from .models import *
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
import pyproj
from shapely.geometry import Polygon

class ParcelleSerializer(GeoFeatureModelSerializer):
    """
    taille_img_x = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    taille_img_y = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        return obj.image.name"""
    area = serializers.SerializerMethodField()
    def get_area(self, obj):
        transformer = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
        coords = [ transformer.transform(point[0], point[1]) for point in obj.region[0] ]
        geod = pyproj.Geod(ellps="WGS84")
        poly = Polygon(coords)
        return abs(geod.geometry_area_perimeter(poly)[0])
    class Meta:
        model = Parcelle
        geo_field = "region"
        fields = [ 'id', 'nom', 'cepage', 'taille', 'pliage', 'area' ]


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

class TacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache
        fields = [ 'id', 'nom' ]

class SaisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saison
        fields = [ 'annee', 'debut', 'fin' ]

class TacheParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TacheParcelle
        fields = [ 'parcelle', 'type_tache' ]