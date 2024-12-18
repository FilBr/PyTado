"""
PyTado interface implementation for hops.tado.com (Tado X).
"""

import logging

from typing import Any

from .my_tado import Tado, Timetable

from ...logger import Logger
from ...exceptions import TadoNotSupportedException
from ...http import (
    Action,
    Http,
    Mode,
    TadoRequest,
    TadoXRequest,
)
from ...zone import TadoZone, TadoXZone


_LOGGER = Logger(__name__)


class TadoX(Tado):
    """Interacts with a Tado thermostat via hops.tado.com (Tado X) API.

    Example usage: http = Http('me@somewhere.com', 'mypasswd')
                   t = TadoX(http)
                   t.get_climate(1) # Get climate, zone 1.
    """

    def __init__(
        self,
        http: Http,
        debug: bool = False,
    ):
        """Class Constructor"""

        super().__init__(http=http, debug=debug)

        if not http.is_x_line:
            raise TadoNotSupportedException(
                "TadoX is only usable with LINE_X Generation"
            )

        if debug:
            _LOGGER.setLevel(logging.DEBUG)
        else:
            _LOGGER.setLevel(logging.WARNING)

        self._http = http

        # Track whether the user's Tado instance supports auto-geofencing,
        # set to None until explicitly set
        self._auto_geofencing_supported = None

    def _create_x_request(self) -> TadoRequest:
        return TadoXRequest()

    def get_devices(self):
        """
        Gets device information.
        """

        request = self._create_x_request()
        request.command = "roomsAndDevices"

        rooms: list[dict[str, Any]] = self._http.request(request)["rooms"]
        devices = [device for room in rooms for device in room["devices"]]

        return devices

    def get_zones(self):
        """
        Gets zones information.
        """

        request = self._create_x_request()
        request.command = "roomsAndDevices"

        return self._http.request(request)["rooms"]

    def get_zone_state(self, zone: int) -> TadoZone:
        """
        Gets current state of Zone as a TadoXZone object.
        """

        return TadoXZone.from_data(zone, self.get_state(zone))

    def get_zone_states(self):
        """
        Gets current states of all zones.
        """

        request = self._create_x_request()
        request.command = "rooms"

        return self._http.request(request)

    def get_state(self, zone):
        """
        Gets current state of Zone.
        """

        request = self._create_x_request()
        request.command = f"rooms/{zone:d}"
        data = self._http.request(request)

        return data

    def get_capabilities(self, zone):
        """
        Gets current capabilities of zone.
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def get_climate(self, zone):
        """
        Gets temp (centigrade) and humidity (% RH) for zone.
        """

        data = self.get_state(zone)["sensorDataPoints"]
        return {
            "temperature": data["insideTemperature"]["value"],
            "humidity": data["humidity"]["percentage"],
        }

    def set_timetable(self, zone: int, timetable: Timetable) -> None:
        """
        Set the Timetable type currently active
        id = 0 : ONE_DAY (MONDAY_TO_SUNDAY)
        id = 1 : THREE_DAY (MONDAY_TO_FRIDAY, SATURDAY, SUNDAY)
        id = 3 : SEVEN_DAY (MONDAY, TUESDAY, WEDNESDAY ...)
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def get_schedule(
        self, zone: int, timetable: Timetable, day=None
    ) -> dict[str, Any]:
        """
        Get the JSON representation of the schedule for a zone.
        Zone has 3 different schedules, one for each timetable (see setTimetable)
        """

        request = self._create_x_request()
        request.command = f"rooms/{zone:d}/schedule"

        return self._http.request(request)

    def set_schedule(self, zone, timetable: Timetable, day, data):
        """
        Set the schedule for a zone, day is required
        """

        request = self._create_x_request()
        request.command = f"rooms/{zone:d}/schedule"
        request.action = Action.SET
        request.payload = data
        request.mode = Mode.OBJECT

        return self._http.request(request)

    def reset_zone_overlay(self, zone):
        """
        Delete current overlay
        """

        request = self._create_x_request()
        request.command = f"rooms/{zone:d}/resumeSchedule"
        request.action = Action.SET

        return self._http.request(request)

    def set_zone_overlay(
        self,
        zone,
        overlay_mode,
        set_temp=None,
        duration=None,
        device_type="HEATING",
        power="ON",
        mode=None,
        fan_speed=None,
        swing=None,
        fan_level=None,
        vertical_swing=None,
        horizontal_swing=None,
    ):
        """
        Set current overlay for a zone
        """

        post_data = {
            "setting": {"type": device_type, "power": power},
            "termination": {"type": overlay_mode},
        }

        if set_temp is not None:
            post_data["setting"]["temperature"] = {
                "value": set_temp,
                "valueRaw": set_temp,
                "precision": 0.1,
            }

        if duration is not None:
            post_data["termination"]["durationInSeconds"] = duration

        request = self._create_x_request()
        request.command = f"rooms/{zone:d}/manualControl"
        request.action = Action.SET
        request.payload = post_data

        return self._http.request(request)

    def get_zone_overlay_default(self, zone: int):
        """
        Get current overlay default settings for zone.
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def get_open_window_detected(self, zone):
        """
        Returns whether an open window is detected.
        """

        data = self.get_state(zone)

        if data["openWindow"] and "activated" in data["openWindow"]:
            return {"openWindowDetected": True}
        else:
            return {"openWindowDetected": False}

    def set_open_window(self, zone):
        """
        Sets the window in zone to open
        Note: This can only be set if an open window was detected in this zone
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def reset_open_window(self, zone):
        """
        Sets the window in zone to closed
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def get_device_info(self, device_id, cmd=""):
        """
        Gets information about devices
        with option to get specific info i.e. cmd='temperatureOffset'
        """

        raise TadoNotSupportedException(
            "This method is not currently supported by the Tado X API"
        )

    def set_temp_offset(self, device_id, offset=0, measure="celsius"):
        """
        Set the Temperature offset on the device.
        """

        request = self._create_x_request()
        request.command = f"roomsAndDevices/devices/{device_id}"
        request.action = Action.CHANGE
        request.payload = {"temperatureOffset": offset}

        return self._http.request(request)
