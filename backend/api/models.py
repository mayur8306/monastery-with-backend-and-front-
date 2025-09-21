from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Monastery(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    visiting_hours = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    elevation = models.FloatField(null=True, blank=True)  # meters
    cultural_notes = models.JSONField(default=dict, blank=True)  # {'en': '...', 'hi': '...', 'ne': '...'}
    languages = models.JSONField(default=list, blank=True)  # eg ['en','hi','ne']
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            slug = base
            i = 1
            while Monastery.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Panorama(models.Model):
    monastery = models.ForeignKey(Monastery, related_name='panoramas', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='panoramas/')
    image_lite = models.ImageField(upload_to='panoramas/lite/', null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    embedding = models.JSONField(null=True, blank=True)  # precomputed CLIP embedding vector
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.monastery.name} - {self.pk}"


class Hotspot(models.Model):
    panorama = models.ForeignKey(Panorama, related_name='hotspots', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pitch = models.FloatField(default=0.0)  # Marzipano coordinates
    yaw = models.FloatField(default=0.0)
    language_content = models.JSONField(default=dict, blank=True)  # {'en':'text','hi':'text','ne':'text'}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.panorama}"


class OfflineExport(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='offline_exports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
