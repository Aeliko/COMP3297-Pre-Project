from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
# Create your models here.


class Location(models.Model):
    location_name = models.CharField('Location Name', max_length=200)
    current_estimated_population = models.PositiveIntegerField(
        'Current Estimated Population', validators=[MinValueValidator(1)])
    api_endpoint = models.URLField('API Endpoint', max_length=200)
    resource_url = models.URLField('URL of Resource', max_length=200)

    def __str__(self) -> str:
        return self.location_name

    def get_absolute_url(self):
        return reverse("location_detail", kwargs={"location_id": self.pk})
