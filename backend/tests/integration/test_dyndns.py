"""Integration tests for the dyndns service."""

import json
import time

from pytest_xdocker.docker import docker


def test_dyndns(tmp_path):
    """The dyndns service should do nothing when records are up to date."""
    settings = tmp_path / "test-settings.txt"
    settings.write_text(
        json.dumps({
            "test": {
                "ip": {
                    "IPv4": "127.0.0.1",
                },
                "protocols": ["IPv4"],
                "last_success": time.time(),
                "provider_name": "test",
                "url_api": "http://localhost:8000",
            },
        }),
        encoding="ascii",
    )
    output = (
        docker.compose()
        .with_project_name("test")
        .run("dyndns")
        .with_build()
        .with_remove()
        .with_volume(
            settings,
            "/test-settings.txt",
        )
        .with_command(
            "/usr/local/bin/domain-connect-dyndns",
            "status",
            "--all",
            "--config",
            "/test-settings.txt",
        )
        .execute(capture_output=True, universal_newlines=True)
    )
    assert "Last DNS succesful update" in output.stdout
