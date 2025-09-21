from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def create_lite_image(image_path, max_width=1024):
    """
    Given a file path to an image, create a resized lite image.
    Returns ContentFile suitable for saving to ImageField.
    """
    img = Image.open(image_path)
    img = img.convert('RGB')
    ratio = min(1.0, max_width / float(img.width))
    if ratio < 1.0:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=75)
    return ContentFile(buffer.getvalue())
