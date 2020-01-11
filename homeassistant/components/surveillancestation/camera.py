"""Support for SurveillanceStation camera streaming."""
import logging
from homeassistant.components.camera import (
    Camera
)
from homeassistant.helpers.aiohttp_client import (
    async_aiohttp_proxy_web,
    async_get_clientsession,
)
from . import DOMAIN as SURVEILLANCESTATION_DOMAIN, DATA_CLIENT, DATA_VERIFY_SSL, DATA_WHITELIST

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the SurveillanceStation cameras."""
    entities = []
    for data in hass.data[SURVEILLANCESTATION_DOMAIN].values():
        surveillance_client = data[DATA_CLIENT]
        whitelist = data[DATA_WHITELIST]
        verify_ssl = data[DATA_VERIFY_SSL]

        cameras = surveillance_client.get_all_cameras()
        if not cameras:
            _LOGGER.warning("Could not fetch cameras from SurveillanceStation host: %s")
            return

        for camera in cameras:
            if not whitelist or camera.name in whitelist:
                _LOGGER.info("Initializing camera %s", camera.camera_id)
                entities.append(SurveillanceStationCamera(surveillance_client, camera.camera_id, verify_ssl))

    add_entities(entities)


class SurveillanceStationCamera(Camera):
    """An implementation of a Surveillance Station based IP camera."""

    def __init__(self, surveillance, camera_id, verify_ssl):
        """Initialize a Surveillance Station camera."""
        super().__init__()
        self._surveillance = surveillance
        self._camera_id = camera_id
        self._verify_ssl = verify_ssl
        self._camera = self._surveillance.get_camera(camera_id)
        self._motion_setting = self._surveillance.get_motion_setting(camera_id)
        self.is_streaming = self._camera.is_enabled

    def camera_image(self):
        """Return bytes of camera image."""
        return self._surveillance.get_camera_image(self._camera_id)

    async def handle_async_mjpeg_stream(self, request):
        """Return a MJPEG stream image response directly from the camera."""
        streaming_url = self._camera.video_stream_url
        websession = async_get_clientsession(self.hass, self._verify_ssl)
        stream_coro = websession.get(streaming_url)
        return await async_aiohttp_proxy_web(self.hass, request, stream_coro)

    @property
    def name(self):
        """Return the name of this device."""
        return self._camera.name

    @property
    def is_recording(self):
        """Return true if the device is recording."""
        return self._camera.is_recording

    @property
    def should_poll(self):
        """Update the recording state periodically."""
        return True

    def update(self):
        """Update the status of the camera."""
        self._surveillance.update()
        self._camera = self._surveillance.get_camera(self._camera.camera_id)
        self._motion_setting = self._surveillance.get_motion_setting(
            self._camera.camera_id
        )
        self.is_streaming = self._camera.is_enabled

    @property
    def motion_detection_enabled(self):
        """Return the camera motion detection status."""
        return self._motion_setting.is_enabled

    def enable_motion_detection(self):
        """Enable motion detection in the camera."""
        self._surveillance.enable_motion_detection(self._camera_id)

    def disable_motion_detection(self):
        """Disable motion detection in camera."""
        self._surveillance.disable_motion_detection(self._camera_id)
