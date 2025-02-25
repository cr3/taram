"""Integration tests for the MySQL service."""

from subprocess import CalledProcessError

from pytest_xdocker.docker import docker
from pytest_xdocker.retry import retry


def test_mysql_service(mysql_service):
    """The MySQL service should allow connection from DBUSER."""
    env = mysql_service.env
    command = docker.exec_(mysql_service.name).with_command(
        "mysql",
        "--execute=SELECT VERSION();",
        f"--user={env['MYSQL_USER']}",
        f"--password={env['MYSQL_PASSWORD']}",
        env["MYSQL_DATABASE"],
    )
    result = retry(command.execute).catching(CalledProcessError)
    assert "MariaDB" in result
