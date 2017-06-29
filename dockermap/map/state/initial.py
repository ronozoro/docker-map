# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import STATE_ABSENT
from .base import DependencyStateGenerator, ContainerBaseState, NetworkBaseState


class InitialContainerState(ContainerBaseState):
    """
    Assumes every container to be absent. This is intended for testing and situations where the actual state
    cannot be determined.
    """
    def inspect(self, instance_alias, config_flags=0):
        # No need to actually make any client call
        pass

    def get_state(self):
        return STATE_ABSENT, 0, {}


class InitialNetworkState(NetworkBaseState):
    """
    Assumes every network to be absent. This is intended for testing and situations where the actual state
    cannot be determined.
    """
    def inspect(self):
        # No need to actually make any client call
        pass

    def get_state(self):
        return STATE_ABSENT, 0, {}


class InitialStateGenerator(DependencyStateGenerator):
    container_state_class = InitialContainerState
    network_state_class = InitialNetworkState
