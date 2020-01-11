"""Support for SurveillanceStation."""
import logging
import requests
from synology.surveillance_station import SurveillanceStation
import voluptuous as vol

from homeassistant.const import (
    ATTR_ID,
    ATTR_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_NAME,
    CONF_URL,
    CONF_TIMEOUT,
    CONF_WHITELIST
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "SurveillanceStation"
DEFAULT_SSL = False
DEFAULT_TIMEOUT = 5
DEFAULT_VERIFY_SSL = True
DOMAIN = "surveillancestation"

DATA_CLIENT = "Client"
DATA_VERIFY_SSL = "VerifySSL"
DATA_WHITELIST = "Whitelist"

HOST_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_WHITELIST, default=[]): cv.ensure_list,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [HOST_CONFIG_SCHEMA])
    },
    extra=vol.ALLOW_EXTRA
)

SERVICE_SET_HOME_MODE = "set_home_mode"
HOME_MODE_AWAY = "away"
HOME_MODE_HOME = "home"
ATTR_HOME_MODE = "home_mode"

SET_HOME_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.string,
        vol.Required(ATTR_HOME_MODE): vol.In([HOME_MODE_AWAY, HOME_MODE_HOME])
    }
)


def setup(hass, config):
    """Set up the SurveillanceStation component."""

    hass.data[DOMAIN] = {}

    success = True

    for conf in config[DOMAIN]:
        host_name = conf.get(CONF_NAME)
        verify_ssl = conf.get(CONF_VERIFY_SSL)
        timeout = conf.get(CONF_TIMEOUT)
        whitelist = conf.get(CONF_WHITELIST)

        try:
            surveillance_client = SurveillanceStation(
                conf.get(CONF_URL),
                conf.get(CONF_USERNAME),
                conf.get(CONF_PASSWORD),
                verify_ssl=verify_ssl,
                timeout=timeout
            )
            hass.data[DOMAIN][host_name] = {}
            hass.data[DOMAIN][host_name][DATA_CLIENT] = surveillance_client
            hass.data[DOMAIN][host_name][DATA_WHITELIST] = whitelist
            hass.data[DOMAIN][host_name][DATA_VERIFY_SSL] = verify_ssl
        except (requests.exceptions.RequestException, ValueError):
            _LOGGER.exception("Error when initializing SurveillanceStation")
            success = False

    def set_home_mode(call):
        """Set the SurveillanceStation home mode to the given state name."""
        ss_id = call.data[ATTR_ID]
        ss_mode = call.data[ATTR_HOME_MODE]

        if ss_id not in hass.data[DOMAIN]:
            _LOGGER.error("Invalid SurveillanceStation host provided: %s", ss_id)
        else:
            ss_id_data = hass.data[DOMAIN][ss_id]
            client = ss_id_data[DATA_CLIENT]
            if not client.set_home_mode(ss_mode == HOME_MODE_HOME):
                _LOGGER.error(
                    "Unable to change SurveillanceStation home mode. Host: %s, mode: %s",
                    ss_id,
                    ss_mode,
                )

    hass.services.register(
        DOMAIN, SERVICE_SET_HOME_MODE, set_home_mode, schema=SET_HOME_MODE_SCHEMA
    )

    return success
