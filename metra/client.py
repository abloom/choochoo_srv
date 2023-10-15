from datetime import datetime
import requests

class MetraClient:
    base_headers = {'Accept': 'application/json'}

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    @property
    def base_url(self) -> str:
        return f"https://{self.username}:{self.password}@gtfsapi.metrarail.com/gtfs"

    def _get(self, url, headers = {}):
        url = self.base_url + url
        return requests.get(url, headers | self.base_headers).json()

    def trip_updates(self) -> list:
        return self._get("/tripUpdates")

    def calendars(self) -> dict:
        return self._get("/schedule/calendar")

    def trips(self) -> dict:
        return self._get("/schedule/trips")

    def stops(self) -> dict:
        return self._get("/schedule/stops")

    def routes(self) -> dict:
        return self._get("/schedule/routes")

    def stop_times(self) -> dict:
        return self._get("/schedule/stop_times")