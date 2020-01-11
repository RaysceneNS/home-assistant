"""Support for setting home mode on SurveillanceStation."""
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.entity import ToggleEntity
from . import DOMAIN as SURVEILLANCESTATION_DOMAIN, DATA_CLIENT

HOME_ICONS = {
    STATE_ON: "mdi:home-account",
    STATE_OFF: "mdi:home-outline"
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the SurveillanceStation switch platform."""
    switches = []
    for data in hass.data[SURVEILLANCESTATION_DOMAIN].values():
        surveillance_client = data[DATA_CLIENT]
        switches.append(SurveillanceStationHomeModeSwitch(surveillance_client))
    add_entities(switches)


class SurveillanceStationHomeModeSwitch(ToggleEntity):
    """Representation of a switch to toggle on/off home mode."""

    def __init__(self, surveillance):
        """Initialize the switch."""
        self._surveillance = surveillance
        self._state = None

    @property
    def should_poll(self):
        """Poll for status regularly."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return "Surveillance Station Home Mode"

    @property
    def state(self):
        """Return the state of the device if any."""
        return self._state

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return HOME_ICONS.get(self.state)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self._surveillance.set_home_mode(True)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._surveillance.set_home_mode(False)

    def update(self):
        """Update Motion Detection state."""
        self._state = STATE_ON if self._surveillance.get_home_mode_status() else STATE_OFF
