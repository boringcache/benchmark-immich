#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVATE = ROOT / "scripts/activate-docker-plan.py"


class ActivateDockerPlanTest(unittest.TestCase):
    def activate(self, *args: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / ".boringcache.toml"
            plan.write_text((ROOT / ".boringcache.toml").read_text())
            subprocess.run(
                [sys.executable, str(ACTIVATE), "--plan", str(plan), *args],
                check=True,
            )
            return tomllib.loads(plan.read_text())

    def test_server_publication_is_resolved_into_direct_docker_argv(self) -> None:
        plan = self.activate(
            "--scenario", "server",
            "--source-sha", "a" * 40,
            "--build-id", "123",
            "--source-ref", "main",
            "--push", "true",
            "--image", "ghcr.io/acme/immich-server:boringcache",
        )
        command = plan["adapters"]["docker"]["command"]
        self.assertEqual(command[:3], ["docker", "buildx", "build"])
        self.assertIn("BUILD_SOURCE_COMMIT=" + "a" * 40, command)
        self.assertIn("ghcr.io/acme/immich-server:boringcache", command)
        self.assertIn("--push", command)

    def test_base_images_ccache_is_selected_in_the_repo_plan(self) -> None:
        plan = self.activate(
            "--scenario", "base-images",
            "--tool-cache", "true",
        )
        docker = plan["adapters"]["docker"]
        self.assertEqual(docker["tool-cache"], ["ccache"])
        self.assertIn("base-images-upstream/server/Dockerfile", docker["command"])
        self.assertEqual(plan["adapters"]["ccache"]["tag"], "immich-ccache-local")


if __name__ == "__main__":
    unittest.main()
