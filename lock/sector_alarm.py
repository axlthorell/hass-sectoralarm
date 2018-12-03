"""
"""
import logging

from homeassistant.components.lock import LockDevice
from homeassistant.const import (ATTR_CODE, STATE_LOCKED, STATE_UNKNOWN,
                                 STATE_UNLOCKED)

import custom_components.sector_alarm as sector_alarm

DEPENDENCIES = ['sector_alarm']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass,
                               config,
                               async_add_entities,
                               discovery_info=None):

    sector_hub = hass.data[sector_alarm.DATA_SA]

    locks = await sector_hub.get_locks()

    if locks is not None:
        async_add_entities(SectorAlarmLock(sector_hub, lock) for lock in locks)


class SectorAlarmLock(LockDevice):
    """Representation of a Sector Alarm lock."""

    def __init__(self, hub, serial):
        self._hub = hub
        self._serial = serial

    @property
    def name(self):
        """Return the serial of the lock."""
        return self._serial

    @property
    def state(self):
        """Return the state of the lock."""
        state = self._hub.lock_states[self._serial]

        if state == 'lock':
            return STATE_LOCKED
        elif state == 'unlock':
            return STATE_UNLOCKED

        return STATE_UNKNOWN

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    @property
    def code_format(self):
        """Return the required six digit code."""
        return None

    async def async_update(self):
        update = self._hub.update()
        if update:
            await update

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        state = self._hub.lock_states[self._serial]
        return state == STATE_LOCKED

    async def async_unlock(self, **kwargs):
        """Send unlock command."""
        state = self._hub.lock_states[self._serial]
        if state == STATE_UNLOCKED:
            return

        await self._hub.unlock(self._serial)

    async def async_lock(self, **kwargs):
        """Send lock command."""
        state = self._hub.lock_states[self._serial]
        if state == STATE_LOCKED:
            return

        await self._hub.lock(self._serial)
