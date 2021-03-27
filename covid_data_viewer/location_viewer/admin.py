from django.contrib import admin

# Register your models here.

from .models import Location


class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'current_estimated_population',
                    'api_endpoint', 'resource_url')


admin.site.register(Location, LocationAdmin)
