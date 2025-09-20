from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MonasteryViewSet, PanoramaUploadView, MatchImageView,
    HotspotViewSet, OfflineDumpView, RoutingView
)

router = DefaultRouter()
router.register('monasteries', MonasteryViewSet, basename='monastery')
router.register('hotspots', HotspotViewSet, basename='hotspot')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-panorama/', PanoramaUploadView.as_view(), name='upload-panorama'),
    path('match-image/', MatchImageView.as_view(), name='match-image'),
    path('offline-dump/', OfflineDumpView.as_view(), name='offline-dump'),
    path('routing/', RoutingView.as_view(), name='routing'),
]
