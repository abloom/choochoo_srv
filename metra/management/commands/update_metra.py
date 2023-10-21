from datetime import time, datetime
from django.core.management.base import BaseCommand
from metra.client import MetraClient
from django.conf import settings
from metra import models
from zoneinfo import ZoneInfo

chicago_tz = ZoneInfo("America/Chicago")
utc_tz = ZoneInfo("UTC")

def _extract_time(time_str):
    return datetime.strptime(time_str, '%H:%M:%S').replace(tzinfo=chicago_tz).astimezone(utc_tz).time()

def from_central_time_string(central_time: str) -> time:
    try:
        return _extract_time(central_time)
    except ValueError:
        # some trips that end up running past midnight have an arrival time larger than 23 hours
        time_parts = central_time.split(":")
        time_parts[0] = str(int(time_parts[0]) - 24).zfill(2)
        adjusted_central_time = ":".join(time_parts)
        return _extract_time(adjusted_central_time)

def batch(iterable, n=1000):
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx+n, length)]

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
            if service:
                service.start_date = calendar["start_date"]
                service.end_date = calendar["end_date"]
            else:
                service = models.Service.objects.create(
                    service_id=service_id,
                    start_date=calendar["start_date"],
                    end_date=calendar["end_date"],
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

            service.save()
            count += 1

        self.stdout.write("Created or updated %d metra.Services" % count)

    def load_routes(self):
        count = 0

        for route_data in self.client.routes():
            route_id = route_data["route_id"]
            route = models.Route.objects.filter(route_id=route_id).first()
            if route:
                route.short_name = route_data["route_short_name"]
                route.long_name = route_data["route_long_name"]
                route.route_color = route_data["route_color"]
                route.text_color = route_data["route_text_color"]
                route.save()
            else:
                route = models.Route.objects.create(
                    route_id=route_id,
                    short_name=route_data["route_short_name"],
                    long_name=route_data["route_long_name"],
                    route_color=route_data["route_color"],
                    text_color=route_data["route_text_color"],
                )

            count += 1

        self.stdout.write("Created or updated %d metra.Routes" % count)

    def load_trips(self):
        count = 0

        routes = {}
        for route in models.Route.objects.all():
            routes[route.route_id] = route

        services = {}
        for service in models.Service.objects.all():
            services[service.service_id] = service

        for trip_batches in batch(self.client.trips()):
            trips = []

            for trip_data in trip_batches:
                trips.append(
                    models.Trip(
                        trip_id = trip_data["trip_id"],
                        direction=trip_data["direction_id"] + 1,
                        route=routes[trip_data["route_id"]],
                        service=services[trip_data["service_id"]],
                    )
                )

            results = models.Trip.objects.bulk_create(
                trips,
                update_conflicts=True,
                unique_fields=['trip_id'],
                update_fields=['direction', 'route', 'service'],
            )

            count += len(results)

        self.stdout.write("Created or updated %d metra.Trips" % count)

    def load_stops(self):
        count = 0

        for stop_data in self.client.stops():
            stop_id = stop_data["stop_id"]
            stop = models.Stop.objects.filter(stop_id=stop_id).first()
            if stop:
                stop.name = stop_data["stop_name"]
                stop.save()
            else:
                stop = models.Stop.objects.create(
                    stop_id=stop_id,
                    name=stop_data["stop_name"],
                )

            count += 1

        self.stdout.write("Created or updated %d metra.Stops" % count)

    def load_stop_times(self):
        count = 0

        stops = {}
        for stop in models.Stop.objects.all():
            stops[stop.stop_id] = stop

        trips = {}
        for trip in models.Trip.objects.all():
            trips[trip.trip_id] = trip

        for stop_time_batches in batch(self.client.stop_times()):
            stop_times = []

            for stop_time_data in stop_time_batches:
                stop_times.append(
                    models.StopTime(
                        stop=stops[stop_time_data["stop_id"]],
                        trip=trips[stop_time_data["trip_id"]],
                        arrival_time=from_central_time_string(stop_time_data["arrival_time"]),
                        departure_time=from_central_time_string(stop_time_data["departure_time"]),
                        stop_sequence=stop_time_data["stop_sequence"],
                    )
                )

            results = models.StopTime.objects.bulk_create(
                stop_times,
                update_conflicts=True,
                unique_fields=["stop", "trip"],
                update_fields=["arrival_time", "departure_time", "stop_sequence"],

            )

            count += len(results)

        self.stdout.write("Created or updated %d metra.StopTime" % count)