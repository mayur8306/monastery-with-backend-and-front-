from django.db import models

class Monastery(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    iframe_url = models.URLField(blank=True, help_text="Google 360° tour iframe URL")
    virtual_image = models.FileField(upload_to='monastery_360/', blank=True, null=True)

    def __str__(self):
        return self.name


# Create your models here.
