"""Integration tests for the MySQL service."""

from subprocess import CalledProcessError

from pytest_xdocker.docker import docker
from pytest_xdocker.retry import retry


def test_mysql_service(env_vars, mysql_service):
    """The MySQL service should allow connection from DBUSER."""
    command = docker.exec_(mysql_service.name).with_command(
        "mysql",
        "--execute=SELECT VERSION();",
        f"--user={env_vars['DBUSER']}",
        f"--password={env_vars['DBPASS']}",
        env_vars["DBNAME"],
    )
    result = retry(command.execute).catching(CalledProcessError)
    assert "MariaDB" in result
