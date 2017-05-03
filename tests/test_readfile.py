# -*- coding: utf-8 -*-
import os
import sys
# needed if using pytest (not needed for py.test)
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../biotracks")

from biotracks import readfile
from pytest import fixture
import pandas as pd


class Data(object):

    def __init__(self):
        self.grouped = []
        self.read_file = None
        directory = os.path.dirname(__file__)
        self.f = os.path.join(directory, "test_files", "test_fake_tracks_tm.xml")
        self.joint_id = 'Track N'


@fixture(scope="class")
def data():
    return Data()


class TestReadFile(object):
    """Read file test."""

    def test_01_import_file(self, data):
        """Test routine read_file"""
        print("ReadFileTest:test_01_read_file")
        assert os.path.exists(data.f)
        data.read_file = readfile.read_file(data.f, {})
        print(data.read_file)
        assert data.read_file is not None
