# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

import docker

from .base import DockerClientWrapper
from .config import ClientConfiguration
from .container import ContainerMap
from .policy import ResumeUpdatePolicy


class MappingDockerClient(object):
    """
    Reflects a :class:`~dockermap.map.container.ContainerMap` instance on a Docker client
    (:class:`~docker.client.Client` or a subclass, e.g. :class:`~dockermap.map.base.DockerClientWrapper`).
    The ``policy_class`` determines if and how dependencies are being considered during creation, starting, stopping,
    and removal of containers.

    If only one container map is provided, it will be the default map for all operations. If multiple container maps
    are used, the list can contain instances of clients to be used. In that case, the ``docker_client`` argument is
    ignored.

    Image names, container status, and dependencies are cached. In order to force a refresh, use :meth:`refresh_names`.
    It is also cleared on every change of ``policy_class``.

    :param container_maps: :class:`~dockermap.map.container.ContainerMap` instance or a tuple or list of such instances
      along with an associated instance.
    :type container_maps: dockermap.map.container.ContainerMap or
      list[dockermap.map.container.ContainerMap]
    :param docker_client: Default :class:`~docker.client.Client` instance.
    :type docker_client: docker.client.Client
    :param clients: Dictionary of client objects, client configurations, or both
    :type clients: dict[unicode, docker.client.Client] or dict[unicode, dockermap.map.config.ClientConfiguration]
      or dict[unicode, (docker.client.Client, dockermap.map.config.ClientConfiguration)]
    :param policy_class: Policy class based on :class:`~dockermap.map.policy.base.BasePolicy` for generating container
      actions.
    :type policy_class: class
    """
    configuration_class = ClientConfiguration
    client_class = DockerClientWrapper

    def __init__(self, container_maps=None, docker_client=None, clients=None, policy_class=ResumeUpdatePolicy):
        def _client_config(obj):
            if isinstance(obj, docker.Client):
                return obj, self.configuration_class.from_client(obj)
            elif isinstance(obj, ClientConfiguration):
                return self.client_class.from_config(obj), obj
            elif isinstance(obj, tuple) and isinstance(obj[0], docker.Client) and isinstance(obj[1], ClientConfiguration):
                return obj
            raise ValueError("Unexpected type of clients item: {0}".format(type(obj)))

        if isinstance(container_maps, ContainerMap):
            self._default_map = container_maps.name
            self._maps = {container_maps.name: container_maps}
        elif isinstance(container_maps, (list, tuple)):
            self._default_map = None
            self._maps = dict((c_map.name, c_map) for c_map in container_maps)
        else:
            raise ValueError("Unexpected type of container_maps argument: {0}".format(type(container_maps)))
        self._clients = dict((client_name, _client_config(client_obj))
                             for client_name, client_obj in six.iteritems(clients)) if clients else dict()
        if docker_client:
            default_name = policy_class.get_default_client_name()
            self._clients[default_name] = _client_config(docker_client)
        self._policy_class = policy_class
        self._policy = None

    def get_policy(self):
        """
        Returns an instance of :attr:`~policy_class`.

        :return: An instance of the current policy class.
        :rtype: dockermap.map.policy.BasePolicy
        """
        if not self._policy:
            self._policy = self._policy_class(self._maps, self._clients)
        return self._policy

    def create(self, container, instances=None, map_name=None, **kwargs):
        """
        Creates container instances for a container configuration.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance name to create. If not specified, will create all instances as specified in the
         configuration (or just one default instance).
        :type instances: tuple or list
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :param kwargs: Additional kwargs. If multiple actions are resulting from this, they will only be applied to
          the main container creation.
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().create_actions(map_name or self._default_map, container, instances, **kwargs)

    def start(self, container, instances=None, map_name=None, **kwargs):
        """
        Starts instances for a container configuration.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to start. If not specified, will start all instances as specified in the
         configuration (or just one default instance).
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :type instances: iterable
        :param kwargs: Additional kwargs. If multiple actions are resulting from this, they will only be applied to
          the main container start.
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().start_actions(map_name or self._default_map, container, instances, **kwargs)

    def restart(self, container, instances=None, map_name=None, **kwargs):
        """
        Restarts instances for a container configuration.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to stop. If not specified, will restart all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :param kwargs: Additional kwargs. If multiple actions are resulting from this, they will only be applied to
          the main container restart.
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().restart_actions(map_name or self._default_map, container, instances, **kwargs)

    def stop(self, container, instances=None, map_name=None, **kwargs):
        """
        Stops instances for a container configuration.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to stop. If not specified, will stop all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :param raise_on_error: Errors on stop and removal may result from Docker volume problems, that do not further
          affect further actions. Such errors are always logged, but do not raise an exception unless this is set to
          ``True``. Please note that 404 errors (on non-existing containers) are always ignored on stop and removal.
        :type raise_on_error: bool
        :param kwargs: Additional kwargs. If multiple actions are resulting from this, they will only be applied to
          the main container stop.
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().stop_actions(map_name or self._default_map, container, instances, **kwargs)

    def remove(self, container, instances=None, map_name=None, **kwargs):
        """
        Remove instances from a container configuration.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to remove. If not specified, will remove all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :param kwargs: Additional kwargs. If multiple actions are resulting from this, they will only be applied to
          the main container removal.
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().remove_actions(map_name or self._default_map, container, instances, **kwargs)

    def startup(self, container, instances=None, map_name=None):
        """
        Start up container instances from a container configuration. Typically this means creating and starting
        containers and their dependencies. Note that not all policy classes necessarily implement this method.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to remove. If not specified, will remove all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().startup_actions(map_name or self._default_map, container, instances)

    def shutdown(self, container, instances=None, map_name=None):
        """
        Shut down container instances from a container configuration. Typically this means stopping and removing
        containers. Note that not all policy classes necessarily implement this method.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to remove. If not specified, will remove all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().shutdown_actions(map_name or self._default_map, container, instances)

    def update(self, container, instances=None, map_name=None):
        """
        Updates instances from a container configuration. Typically this means restarting or recreating containers based
        on detected changes in the configuration or environment.  Note that not all policy classes necessarily implement
        this method.

        :param container: Container name.
        :type container: unicode
        :param instances: Instance names to remove. If not specified, will remove all instances as specified in the
         configuration (or just one default instance).
        :type instances: iterable
        :param map_name: Container map name. Optional - if not provided the default map is used.
        :type map_name: unicode
        :return: Return values of created main containers.
        :rtype: list[(unicode, dict)]
        """
        return self.get_policy().update_actions(map_name or self._default_map, container, instances)

    def refresh_names(self):
        """
        Invalidates the policy name and status cache.
        """
        self._policy = None

    def list_persistent_containers(self, map_name=None):
        """
        Lists the names of all persistent containers on the specified map or all maps. Attached containers are always
        considered persistent.

        :param map_name: Container map name. Optional, only returns persistent containers from the specified map.
        :type map_name: unicode
        :return: List of container names.
        :rtype: list[unicode]
        """
        def _container_names():
            for c_map in maps:
                for container, config in c_map:
                    for ac in config.attaches:
                        yield cname_func(c_map.name, ac)
                    if config.persistent:
                        if config.instances:
                            for ci in config.instances:
                                yield cname_func(c_map.name, container, ci)
                        else:
                            yield cname_func(c_map.name, container)

        cname_func = self._policy_class.cname
        maps = (self._maps[map_name], ) if map_name else self._maps.values()
        return list(_container_names())

    @property
    def maps(self):
        """
        Container maps.

        :return: A dictionary with container map names as keys, and container map and client as values.
        :rtype: dict[unicode, MapClient]
        """
        return self._maps

    @property
    def default_map(self):
        """
        The default map to use for any actions, if not otherwise specified.

        :return: Container map name.
        :rtype: unicode
        """
        return self._default_map

    @default_map.setter
    def default_map(self, value):
        if value in self._maps:
            raise ValueError("Default name must match an available map name.")
        self._default_map = value

    @property
    def policy_class(self):
        """
        The policy class, that transforms commands into actions on containers, considering potential dependencies.

        :return: Subclass of :class:`~dockermap.map.policy.base.BasePolicy`.
        :rtype: class
        """
        return self._policy_class

    @policy_class.setter
    def policy_class(self, value):
        self._policy = None
        self._policy_class = value
