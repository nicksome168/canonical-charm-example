#!/usr/bin/env python3
# Copyright 2024 Ubuntu
# See LICENSE file for licensing details.

"""Charm the application."""
import os
import logging
import ops

import requests_unixsocket

logger = logging.getLogger(__name__)


class MyCharmCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.ActiveStatus()

    def _on_install(self, event: ops.InstallEvent):
        """Handle install event"""
        self.unit.status = ops.MaintenanceStatus("Installing microsample snap")
        channel = self.config.get('channel')
        if channel in ['beta', 'edge', 'candidate', 'stable']:
            os.system(f"snap install my-charm --{channel}")
            self.unit.status = ops.ActiveStatus("Ready")
        else:
            self.unit.status = ops.BlockStatus("Invalid channel configured.")

    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        channel = self.config.get('channel')
        if channel in ['beta', 'edge', 'candidate', 'stable']:
            os.system(f"snap refresh my-charm --{channel}")
            workload_version = self._getWorkloadVersion()
            self.unit.set_workload_version(workload_version)
            self.unit.status = ops.ActiveStatus(f"Ready at {channel}")
        else:
            self.unit.status = ops.BlockStatus("Invalid channel configured.")

    def _getWorkloadVersion(self):
        """Get the my-charm workload version from the snapd API via unix-socket"""
        snap_name = "my-charm"
        snapd_url = f"http+unix://%2Frun%2Fsnapd.socket/v2/snaps/{snap_name}"
        session = requests_unixsocket.Session()
        # Use the requests library to send a GET request over the Unix domain socket
        response = session.get(snapd_url)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            workload_version = data["result"]["version"]
        else:
            workload_version = "unknown"
            print(f"Failed to retrieve Snap apps. Status code: {response.status_code}")
        return workload_version


if __name__ == "__main__":  # pragma: nocover
    ops.main(MyCharmCharm)  # type: ignore
