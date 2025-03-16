from .models import Parcelle
from rest_framework import serializers
import json

class ParcelleSerializer(serializers.HyperlinkedModelSerializer):
    region = serializers.SerializerMethodField()
    cepage = serializers.SlugRelatedField(slug_field='nom', read_only=True)
    taille = serializers.SlugRelatedField(slug_field='nom', read_only=True)
    pliage = serializers.SlugRelatedField(slug_field='nom', read_only=True)
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