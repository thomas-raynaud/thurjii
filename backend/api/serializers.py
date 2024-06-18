from .models import Parcelle
from rest_framework import serializers

class ParcelleSerializer(serializers.HyperlinkedModelSerializer):
    loc_x = serializers.DecimalField(max_digits=8, decimal_places=5, coerce_to_string=False)
    loc_y = serializers.DecimalField(max_digits=8, decimal_places=5, coerce_to_string=False)
    loc_r = serializers.DecimalField(max_digits=8, decimal_places=5, coerce_to_string=False)
    taille_img_x = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    taille_img_y = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.name

    class Meta:
        model = Parcelle
        fields = [ 'id', 'url', 'nom', 'loc_x', 'loc_y', 'loc_z', 'loc_r', 'taille_img_x', 'taille_img_y', 'image' ]