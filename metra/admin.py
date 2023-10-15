from django.contrib import admin
from metra import models

admin.site.register(models.Service)
admin.site.register(models.Route)
admin.site.register(models.Trip)
admin.site.register(models.Stop)
admin.site.register(models.StopTime)
admin.site.register(models.RouteToDisplay)
admin.site.register(models.StopToDisplay)