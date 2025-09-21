from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from .models import Monastery, Panorama, Hotspot, OfflineExport
from .serializers import MonasterySerializer, PanoramaSerializer, HotspotSerializer, OfflineExportSerializer
from .tasks import process_panorama
import tempfile
import zipfile
import json
import os
import numpy as np
from PIL import Image

class MonasteryViewSet(viewsets.ModelViewSet):
    queryset = Monastery.objects.all()
    serializer_class = MonasterySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'cultural_notes']
    ordering_fields = ['name', 'elevation']

class PanoramaUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        monastery_key = request.data.get('monastery')
        image_file = request.data.get('image')
        is_primary = request.data.get('is_primary', False)
        force = request.query_params.get('force', '0') == '1'

        if not monastery_key or not image_file:
            return Response({'detail': 'monastery and image are required'}, status=400)

        # Lookup monastery by id or slug
        monastery = None
        if monastery_key.isdigit():
            monastery = get_object_or_404(Monastery, id=int(monastery_key))
        else:
            monastery = get_object_or_404(Monastery, slug=monastery_key)

        pano = Panorama.objects.create(monastery=monastery, image=image_file, is_primary=is_primary)

        # Defer heavy processing to async task
        process_panorama.delay(pano.id)

        return Response(PanoramaSerializer(pano).data, status=201)


class MatchImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        image_file = request.data.get('image')
        if not image_file:
            return Response({'detail': 'image required'}, status=400)

        pil = Image.open(image_file).convert('RGB')
        from .services import CLIPService
        query_emb = np.array(CLIPService.get_image_embedding(pil))

        best, best_score = None, -1.0
        for p in Panorama.objects.exclude(embedding__isnull=True):
            emb = np.array(p.embedding)
            score = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-9))
            if score > best_score:
                best, best_score = p, score

        if not best:
            return Response({'match': None})
        data = PanoramaSerializer(best).data
        data['score'] = best_score
        data['monastery'] = MonasterySerializer(best.monastery).data
        return Response(data)


class HotspotViewSet(viewsets.ModelViewSet):
    queryset = Hotspot.objects.all()
    serializer_class = HotspotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OfflineDumpView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        z = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)

        monasteries = [MonasterySerializer(m).data for m in Monastery.objects.all()]
        meta_bytes = json.dumps({'monasteries': monasteries}, ensure_ascii=False).encode('utf-8')
        z.writestr('monasteries.json', meta_bytes)

        for p in Panorama.objects.all():
            if p.image_lite and p.image_lite.path:
                arcname = f"panoramas/lite/{os.path.basename(p.image_lite.path)}"
                try:
                    z.write(p.image_lite.path, arcname)
                except Exception:
                    pass

        z.close()
        tmp.seek(0)
        content = open(tmp.name, 'rb').read()
        export = OfflineExport.objects.create(name=f"export_{int(os.path.getmtime(tmp.name))}")
        export.file.save(f"offline_export_{export.pk}.zip", ContentFile(content))
        export.save()
        os.unlink(tmp.name)
        return Response(OfflineExportSerializer(export).data, status=201)


class RoutingView(APIView):
    """
    Integrate with OpenRouteService or similar for mountain-aware routing.
    For now, simple haversine + crude time estimate.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            start_lat = float(request.query_params['start_lat'])
            start_lng = float(request.query_params['start_lng'])
            end_lat = float(request.query_params['end_lat'])
            end_lng = float(request.query_params['end_lng'])
            mode = request.query_params.get('mode','driving')
        except Exception:
            return Response({'detail':'missing or invalid parameters'}, status=400)

        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        dlat = radians(end_lat - start_lat)
        dlng = radians(end_lng - start_lng)
        a = sin(dlat/2)**2 + cos(radians(start_lat))*cos(radians(end_lat))*sin(dlng/2)**2
        c = 2*atan2(sqrt(a), sqrt(1-a))
        dist_km = R*c

        travel_time_min = dist_km / (30 if mode == 'driving' else 5) * 60  # crude estimate

        return Response({'distance_km': round(dist_km,3), 'travel_time_min': int(travel_time_min), 'mode': mode})

