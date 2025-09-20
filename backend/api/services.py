from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import threading

class CLIPService:
    _model = None
    _processor = None
    _lock = threading.Lock()

    @classmethod
    def load_model(cls):
        with cls._lock:
            if cls._model is None or cls._processor is None:
                cls._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                cls._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                cls._model.eval()
        return cls._model, cls._processor

    @classmethod
    def get_image_embedding(cls, pil_image: Image.Image):
        model, processor = cls.load_model()
        inputs = processor(images=pil_image, return_tensors="pt")
        with torch.no_grad():
            img_feats = model.get_image_features(**inputs)
        img_feats = img_feats / img_feats.norm(p=2, dim=-1, keepdim=True)
        return img_feats[0].cpu().numpy().tolist()

    @classmethod
    def verify_monastery(cls, pil_image: Image.Image, threshold=0.14) -> bool:
        model, processor = cls.load_model()
        inputs = processor(
            text=["a photo of a Buddhist monastery"],
            images=pil_image,
            return_tensors="pt",
            padding=True
        )
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        prob = logits_per_image.softmax(dim=1)[0][0].item()
        return prob >= threshold
