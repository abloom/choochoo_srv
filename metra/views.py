from collections import defaultdict
from pprint import pprint
from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import ListView
from metra import models
from datetime import date

class BidirectionalStop:
    def __init__(self) -> None:
       self.times = {
           1: [],
           2: [],
       }

    def add_stop_time(self, stop_time):
        direction = stop_time.trip.direction
        self.times[direction].append(stop_time)

class StopTimeView(ListView):
    model = models.StopTime

    def get_queryset(self) -> QuerySet[Any]:
        base_queryset = super().get_queryset().prefetch_related('stop', 'trip', 'trip__route').order_by('trip__route', 'stop', 'stop_sequence', 'arrival_time')
        today = date.today()
        day_of_week = models.DayOfTheWeek.objects.get(name=today.strftime("%A"))

        queryset = None
        for route_to_display in models.RouteToDisplay.objects.prefetch_related("stops_to_display").all():
            additional_queryset = base_queryset.filter(
                trip__route__route_id=route_to_display.route_id,
                trip__service__start_date__lte=today,
                trip__service__end_date__gte=today,
                trip__service__days_of_the_week=day_of_week,
            )

            stop_ids = route_to_display.stops_to_display.values_list("stop_id", flat=True)
            if stop_ids:
                additional_queryset = additional_queryset.filter(stop__stop_id__in=stop_ids)

            if queryset:
                queryset = queryset | additional_queryset
            else:
                queryset = additional_queryset

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        stop_order_by_route = defaultdict(list)
        stop_times_by_route_and_stop = defaultdict(lambda: defaultdict(BidirectionalStop))

        for stop_time in self.object_list:
            route = stop_time.trip.route
            stop = stop_time.stop

            stop_times_by_route_and_stop[route][stop].add_stop_time(stop_time)
            if stop not in stop_order_by_route[route]:
                stop_order_by_route[route].append(stop)

        context["stop_times_by_route_and_stop"] = dict(stop_times_by_route_and_stop)
        context["stop_order_by_route"] = dict(stop_order_by_route)

        return context