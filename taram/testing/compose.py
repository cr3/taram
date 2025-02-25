"""Compose server module."""

from contextlib import contextmanager
from datetime import datetime

from attrs import define
from more_itertools import only
from pytest_xdocker.docker import DockerContainer
from pytest_xdocker.process import ProcessData, ProcessServer
from pytest_xdocker.xdocker import xdocker


@define(frozen=True)
class ComposeService:
    """Compose service.

    :param name: Name of the compose service container.
    """

    name: str

    @property
    def container(self):
        return DockerContainer(self.name)

    @property
    def container_id(self):
        return self.container.inspect["Id"]

    @property
    def env(self):
        env = self.container.inspect["Config"]["Env"]
        return dict(e.split("=", 1) for e in env)

    @property
    def ip(self):
        network_settings = self.container.inspect["NetworkSettings"]
        network = only(network_settings["Networks"].values())
        return network["IPAddress"]

    @property
    def started_at(self):
        started_at = self.container.inspect["State"]["StartedAt"]
        return datetime.fromisoformat(started_at)


class ComposeServer(ProcessServer):
    def __init__(self, pattern, project="test", env_file="/dev/null", **kwargs):
        """Initilize a compose server."""
        super().__init__(**kwargs)
        self.pattern = pattern
        self.project = project
        self.env_file = env_file

    def __repr__(self):
        return "{cls}(pattern={pattern!r}, project={project!r})".format(
            cls=self.__class__.__name__,
            pattern=self.pattern,
            project=self.project,
        )

    def full_name(self, name):
        return f"{self.project}-{name}-1"

    def prepare_func(self, controldir):
        """Prepare the function to run the compose service."""
        full_name = self.full_name(controldir.basename)
        command = (
            xdocker.compose()
            .with_project_name(self.project)
            .with_env_file(self.env_file)
            .run(controldir.basename)
            .with_name(full_name)
            .with_build()
            .with_remove()
        )

        return ProcessData(self.pattern, command)

    @contextmanager
    def run(self, name):
        """Return an `ComposeService` to the running service."""
        with super().run(name):
            full_name = self.full_name(name)
            yield ComposeService(full_name)
