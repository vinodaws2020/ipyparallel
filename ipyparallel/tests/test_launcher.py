"""Tests for launchers

Doesn't actually start any subprocesses, but goes through the motions of constructing
objects, which should test basic config.
"""
import logging
import os
import shutil
import sys
import tempfile
from unittest import TestCase

import pytest
from ipython_genutils.py3compat import string_types
from traitlets.config import Config

from ipyparallel.cluster import launcher


# -------------------------------------------------------------------------------
# TestCase Mixins
# -------------------------------------------------------------------------------


class LauncherTest:
    """Mixin for generic launcher tests"""

    def setUp(self):
        self.profile_dir = tempfile.mkdtemp(prefix="profile_")

    def tearDown(self):
        shutil.rmtree(self.profile_dir)

    @property
    def config(self):
        return Config()

    def build_launcher(self, **kwargs):
        kw = dict(
            work_dir=self.profile_dir,
            profile_dir=self.profile_dir,
            config=self.config,
            cluster_id='',
            log=logging.getLogger(),
        )
        kw.update(kwargs)
        return self.launcher_class(**kw)

    def test_profile_dir_arg(self):
        launcher = self.build_launcher()
        self.assertTrue("--profile-dir" in launcher.cluster_args)
        self.assertTrue(self.profile_dir in launcher.cluster_args)

    def test_cluster_id_arg(self):
        launcher = self.build_launcher()
        self.assertTrue("--cluster-id" in launcher.cluster_args)
        idx = launcher.cluster_args.index("--cluster-id")
        self.assertEqual(launcher.cluster_args[idx + 1], '')
        launcher.cluster_id = 'foo'
        self.assertEqual(launcher.cluster_args[idx + 1], 'foo')

    def test_args(self):
        launcher = self.build_launcher()
        for arg in launcher.args:
            self.assertTrue(isinstance(arg, string_types), str(arg))


class BatchTest:
    """Tests for batch-system launchers (LSF, SGE, PBS)"""

    def test_batch_template(self):
        launcher = self.build_launcher()
        batch_file = os.path.join(self.profile_dir, launcher.batch_file_name)
        self.assertEqual(launcher.batch_file, batch_file)
        launcher.write_batch_script(1)
        self.assertTrue(os.path.isfile(batch_file))


class SSHTest:
    """Tests for SSH launchers"""

    def test_cluster_id_arg(self):
        pytest.skip("SSH Launchers don't support cluster ID")

    def test_remote_profile_dir(self):
        cfg = Config()
        launcher_cfg = getattr(cfg, self.launcher_class.__name__)
        launcher_cfg.remote_profile_dir = "foo"
        launcher = self.build_launcher(config=cfg)
        self.assertEqual(launcher.remote_profile_dir, "foo")

    def test_remote_profile_dir_default(self):
        launcher = self.build_launcher()
        self.assertEqual(launcher.remote_profile_dir, self.profile_dir)


# -------------------------------------------------------------------------------
# Controller Launcher Tests
# -------------------------------------------------------------------------------


class ControllerLauncherTest(LauncherTest):
    """Tests for Controller Launchers"""

    pass


class TestLocalControllerLauncher(ControllerLauncherTest, TestCase):
    launcher_class = launcher.LocalControllerLauncher


class TestMPIControllerLauncher(ControllerLauncherTest, TestCase):
    launcher_class = launcher.MPIControllerLauncher


class TestPBSControllerLauncher(BatchTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.PBSControllerLauncher


class TestSlurmControllerLauncher(BatchTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.SlurmControllerLauncher


class TestSGEControllerLauncher(BatchTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.SGEControllerLauncher


class TestLSFControllerLauncher(BatchTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.LSFControllerLauncher


class TestHTCondorControllerLauncher(BatchTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.HTCondorControllerLauncher


class TestSSHControllerLauncher(SSHTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.SSHControllerLauncher


# -------------------------------------------------------------------------------
# Engine Set Launcher Tests
# -------------------------------------------------------------------------------


class EngineSetLauncherTest(LauncherTest):
    """Tests for EngineSet launchers"""

    pass


class TestLocalEngineSetLauncher(EngineSetLauncherTest, TestCase):
    launcher_class = launcher.LocalEngineSetLauncher


class TestMPIEngineSetLauncher(EngineSetLauncherTest, TestCase):
    launcher_class = launcher.MPIEngineSetLauncher


class TestPBSEngineSetLauncher(BatchTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.PBSEngineSetLauncher


class TestSlurmEngineSetLauncher(BatchTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.SlurmEngineSetLauncher


class TestSGEEngineSetLauncher(BatchTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.SGEEngineSetLauncher


class TestLSFEngineSetLauncher(BatchTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.LSFEngineSetLauncher


class TestHTCondorEngineSetLauncher(BatchTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.HTCondorEngineSetLauncher


class TestSSHEngineSetLauncher(EngineSetLauncherTest, TestCase):
    launcher_class = launcher.SSHEngineSetLauncher

    def test_cluster_id_arg(self):
        pytest.skip("SSH Launchers don't support cluster ID")


class TestSSHProxyEngineSetLauncher(SSHTest, LauncherTest, TestCase):
    launcher_class = launcher.SSHProxyEngineSetLauncher


class TestSSHEngineLauncher(SSHTest, LauncherTest, TestCase):
    launcher_class = launcher.SSHEngineLauncher


# -------------------------------------------------------------------------------
# Windows Launcher Tests
# -------------------------------------------------------------------------------


class WinHPCTest:
    """Tests for WinHPC Launchers"""

    def test_batch_template(self):
        launcher = self.build_launcher()
        job_file = os.path.join(self.profile_dir, launcher.job_file_name)
        self.assertEqual(launcher.job_file, job_file)
        launcher.write_job_file(1)
        self.assertTrue(os.path.isfile(job_file))


class TestWinHPCControllerLauncher(WinHPCTest, ControllerLauncherTest, TestCase):
    launcher_class = launcher.WindowsHPCControllerLauncher


class TestWinHPCEngineSetLauncher(WinHPCTest, EngineSetLauncherTest, TestCase):
    launcher_class = launcher.WindowsHPCEngineSetLauncher
