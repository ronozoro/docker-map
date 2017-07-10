# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple


INITIAL_START_TIME = '0001-01-01T00:00:00Z'

STATE_ABSENT = 'absent'     # Does not exist.
STATE_PRESENT = 'present'   # Exists but is not running.
STATE_RUNNING = 'running'   # Exists and is running.

STATE_FLAG_INITIAL = 1               # Container is present but has never been started.
STATE_FLAG_RESTARTING = 1 << 1       # Container is not running, but in the process of restarting.
STATE_FLAG_NONRECOVERABLE = 1 << 10  # Container is stopped with an error that cannot be solved through restarting.
STATE_FLAG_OUTDATED = 1 << 11        # Container in any base state does not correspond with current config.

ConfigState = namedtuple('ConfigState', ['client_name', 'map_name', 'config_type',
                                         'config_name', 'instance_name', 'config_flags', 'base_state',
                                         'state_flags', 'extra_data'])
