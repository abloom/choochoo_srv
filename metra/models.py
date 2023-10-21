from django.db import models

class DayOfTheWeek(models.Model):
    name = models.TextField(max_length=10)

# Calendar
class Service(models.Model):
    service_id = models.CharField(max_length=32, unique=True)
    days_of_the_week = models.ManyToManyField("metra.DayOfTheWeek")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return self.service_id

class Route(models.Model):
    route_id = models.CharField(max_length=12, unique=True)
    short_name = models.CharField(max_length=32)
    long_name = models.CharField(max_length=128)
    route_color = models.CharField(max_length=6)
    text_color = models.CharField(max_length=6)

    def __str__(self) -> str:
        return self.route_id

Direction = models.IntegerChoices("Direction", "OUTBOUND INBOUND")

class Trip(models.Model):
    route = models.ForeignKey("metra.Route", on_delete=models.CASCADE)
    service = models.ForeignKey("metra.Service", on_delete=models.CASCADE)
    trip_id = models.CharField(max_length=64, unique=True)
    direction = models.IntegerField(choices=Direction.choices)

    def __str__(self) -> str:
        return self.trip_id

class Stop(models.Model):
    stop_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.stop_id

class StopTime(models.Model):
    trip = models.ForeignKey("metra.Trip", on_delete=models.CASCADE)
    stop = models.ForeignKey("metra.Stop", on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_sequence = models.IntegerField()

    class Meta:
        ordering = ["stop_sequence"]
        unique_together = ["trip", "stop"]

    def __str__(self) -> str:
        return f"{self.trip} - {self.stop}"

class RouteToDisplay(models.Model):
    route_id = models.CharField(max_length=12)

    def __str__(self) -> str:
        return f"{self.route_id}"

class StopToDisplay(models.Model):
    stop_id = models.CharField(max_length=64)
    route_to_display = models.ForeignKey("metra.RouteToDisplay", related_name="stops_to_display", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.stop_id}"