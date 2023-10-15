from datetime import time
from django.core.management.base import BaseCommand
from metra.client import MetraClient
from django.conf import settings
from metra import models

def from_iso_to_time(iso_time: str) -> time:
    try:
        return time.fromisoformat(iso_time)
    except ValueError:
        # some trips that end up running past midnight have an arrival time larger than 23 hours
        time_parts = iso_time.split(":")
        time_parts[0] = str(int(time_parts[0]) - 24).zfill(2)
        return time.fromisoformat(":".join(time_parts))

class Command(BaseCommand):
    help = 'Displays current time'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client = MetraClient(settings.METRA_USER, settings.METRA_PASS)

    def handle(self, *args, **kwargs):
        self.load_calendars()
        self.load_routes()
        self.load_trips()
        self.load_stops()
        self.load_stop_times()

    def load_calendars(self):
        count = 0

        for calendar in self.client.calendars():
            service_id = calendar["service_id"]
            service = models.Service.objects.filter(service_id=service_id).first()
            if not service:
                service = models.Service.objects.create(
                    service_id=service_id,
                    start_date = calendar["start_date"],
                    end_date = calendar["end_date"],
                )

            if calendar["monday"]:
                service.days_of_the_week.add(1)
            else:
                service.days_of_the_week.remove(1)

            if calendar["tuesday"]:
                service.days_of_the_week.add(2)
            else:
                service.days_of_the_week.remove(2)

            if calendar["wednesday"]:
                service.days_of_the_week.add(3)
            else:
                service.days_of_the_week.remove(3)

            if calendar["thursday"]:
                service.days_of_the_week.add(4)
            else:
                service.days_of_the_week.remove(4)

            if calendar["friday"]:
                service.days_of_the_week.add(5)
            else:
                service.days_of_the_week.remove(5)

            if calendar["saturday"]:
                service.days_of_the_week.add(6)
            else:
                service.days_of_the_week.remove(6)

            if calendar["sunday"]:
                service.days_of_the_week.add(7)
            else:
                service.days_of_the_week.remove(7)

            count += 1

        self.stdout.write("Created or updated %d metra.Services" % count)

    def load_routes(self):
        count = 0

        for route_data in self.client.routes():
            route_id = route_data["route_id"]
            route = models.Route.objects.filter(route_id=route_id).first()
            if not route:
                route = models.Route.objects.create(
                    route_id=route_id,
                    short_name=route_data["route_short_name"],
                    long_name=route_data["route_long_name"],
                    route_color=route_data["route_color"],
                    text_color=route_data["route_text_color"]
                )

            count += 1

        self.stdout.write("Created or updated %d metra.Routes" % count)

    def load_trips(self):
        count = 0

        for trip_data in self.client.trips():
            trip_id = trip_data["trip_id"]
            trip = models.Trip.objects.filter(trip_id=trip_id).first()
            if not trip:
                trip = models.Trip.objects.create(
                    trip_id=trip_id,
                    direction=trip_data["direction_id"],
                    route=models.Route.objects.get(route_id=trip_data["route_id"]),
                    service=models.Service.objects.get(service_id=trip_data["service_id"])
                )

            count += 1

        self.stdout.write("Created or updated %d metra.Trips" % count)

    def load_stops(self):
        count = 0

        for stop_data in self.client.stops():
            stop_id = stop_data["stop_id"]
            stop = models.Stop.objects.filter(stop_id=stop_id).first()
            if not stop:
                stop = models.Stop.objects.create(
                   stop_id=stop_id,
                   name=stop_data["stop_name"]
                )

            count += 1

        self.stdout.write("Created or updated %d metra.Stops" % count)

    def load_stop_times(self):
        count = 0

        for stop_time_data in self.client.stop_times():
            stop = models.Stop.objects.get(stop_id=stop_time_data["stop_id"])
            trip = models.Trip.objects.get(trip_id=stop_time_data["trip_id"])
            stop_time = models.StopTime.objects.filter(stop=stop, trip=trip).first()
            if not stop_time:
                stop_time = models.StopTime.objects.create(
                    stop=stop,
                    trip=trip,
                    arrival_time=from_iso_to_time(stop_time_data["arrival_time"]),
                    departure_time=from_iso_to_time(stop_time_data["departure_time"]),
                    stop_sequence=stop_time_data["stop_sequence"],
                )

            count += 1

        self.stdout.write("Created or updated %d metra.StopTime" % count)