from rest_framework import serializers
from .models import Monastery, Panorama, Hotspot, OfflineExport

class HotspotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotspot
        fields = ['id','title','description','pitch','yaw','language_content','created_at']

class PanoramaSerializer(serializers.ModelSerializer):
    hotspots = HotspotSerializer(many=True, read_only=True)
    class Meta:
        model = Panorama
        fields = ['id','monastery','image','image_lite','is_primary','embedding','created_at','hotspots']

class MonasterySerializer(serializers.ModelSerializer):
    panoramas = PanoramaSerializer(many=True, read_only=True)
    class Meta:
        model = Monastery
        fields = [
            'id','name','slug','description','visiting_hours',
            'latitude','longitude','elevation','cultural_notes','languages','panoramas'
        ]

class OfflineExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineExport
        fields = ['id','name','file','created_at']
