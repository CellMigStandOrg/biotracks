# -*- coding: utf-8 -*-
import os
import sys
# needed if using pytest (not needed for py.test)
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dpkg")

from dpkg import readfile
from pytest import fixture
import pandas as pd


class Data(object):

    def __init__(self):
        self.grouped = []
        self.read_file = None
        directory = os.path.dirname(__file__)
        self.f = os.path.join(directory, "test_files", "tracks_ctr.csv")
        self.n = 20
        self.joint_id = 'Track N'


@fixture(scope="class")
def data():
    return Data()


class TestReadFile(object):
    """Read file test."""

    def test_01_import_file(self, data):
        """Test routine import_file"""
        print("ReadFileTest:test_01_import_file")
        assert os.path.exists(data.f)
        data.read_file = readfile.import_file(data.f, data.n)
        print(data.read_file)
        assert data.read_file is not None

    def test_02_group_by_joint_id(self, data):
        """Test routine group_by_joint_id"""
        data.grouped = readfile.group_by_joint_id(
            data.read_file, data.joint_id)
        assert data.grouped is not None
        assert isinstance(data.grouped, pd.core.groupby.DataFrameGroupBy)
        print("ReadFileTest:test_02_group_by_joint_id")

    def test_03_split_in_objs_evnts(self, data):
        """Test routine split_in_objs_evnts"""
        dict_ = readfile.split_in_objs_evnts(data.joint_id, data.grouped)
        assert dict_ is not None
        for key in dict_:
            print("key: %s , value: %s" % (key, dict_[key]))
        print("ReadFileTest:test_03_split_in_objs_evnts")
