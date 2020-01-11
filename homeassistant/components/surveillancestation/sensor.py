"""Support for SurveillanceStation sensors."""
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.entity import Entity
from . import DOMAIN as SURVEILLANCESTATION_DOMAIN, DATA_CLIENT


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the SurveillanceStation sensor platform."""
    sensors = []
    for data in hass.data[SURVEILLANCESTATION_DOMAIN].values():
        surveillance_client = data[DATA_CLIENT]
        sensors.append(SSSensorHomeMode(surveillance_client))
    add_entities(sensors)


class SSSensorHomeMode(Entity):
    """Get the SurveillanceStation home mode."""

    def __init__(self, client):
        """Initialize home mode sensor."""
        self._state = None
        self._client = client

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Home Mode"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update the sensor."""
        self._state = STATE_ON if self._client.get_home_mode_status() else STATE_OFF
