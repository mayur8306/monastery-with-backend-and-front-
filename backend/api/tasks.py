from celery import shared_task
from .models import Panorama
from .services import CLIPService
from .utils import create_lite_image
from django.core.files.base import ContentFile
import os
from PIL import Image

@shared_task
def process_panorama(panorama_id):
    try:
        pano = Panorama.objects.get(id=panorama_id)
        pil = Image.open(pano.image.path).convert('RGB')

        # Verify image (optional, can skip or log)
        if not CLIPService.verify_monastery(pil):
            # Log warning or mark pano invalid
            pass

        # Generate embedding
        embedding = CLIPService.get_image_embedding(pil)
        pano.embedding = embedding

        # Create lite image
        lite_content = create_lite_image(pano.image.path)
        lite_name = f"lite_{os.path.basename(pano.image.name)}"
        pano.image_lite.save(lite_name, lite_content)

        pano.save()
    except Exception as e:
        # Log error
        pass
