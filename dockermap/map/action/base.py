# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import abstractmethod

from six import with_metaclass

from ..policy import ABCPolicyUtilMeta, PolicyUtil


class AbstractActionGenerator(with_metaclass(ABCPolicyUtilMeta, PolicyUtil)):
    """
    Abstract base class for action generators, which determine what actions are to be executed based on current
    container states.
    """
    @abstractmethod
    def get_state_actions(self, states, **kwargs):
        """
        Generates actions from a container configuration state.

        :param states: Container configuration states.
        :type states: collections.Iterable[dockermap.map.state.ConfigState]
        :param kwargs: Additional keyword arguments.
        :return: Actions on the client, map, and configurations.
        :rtype: list[dockermap.map.action.ItemAction]
        """
        pass
