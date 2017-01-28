# -*- coding: utf-8 -*-
import os
import sys
# needed if using pytest (not needed for py.test)
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dpkg")

from dpkg import readfile
import unittest
import pandas as pd


class ReadFileTest(unittest.TestCase):
    """Read file test."""

    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        print("ReadFileTest:setUp_:begin")
        self.grouped = []
        self.read_file = None
        self.f = "test_files/tracks_ctr.csv"
        self.n = 20
        self.joint_id = 'Track N'
        print("ReadFileTest:setUp_:end")

    # ending the test
    def tearDown(self):
        """Cleaning up after the test"""
        print("ReadFileTest:tearDown_:begin")
        # do something...
        print("ReadFileTest:tearDown_:end")

    # test routine import_file
    def test_01_import_file(self):
        """Test routine import_file"""
        print("ReadFileTest:test_01_import_file")
        self.assertTrue(os.path.exists(self.f))
        self.read_file = readfile.import_file(self.f, self.n)
        print(self.read_file)
        assert self.read_file is not None

    # test routine group_by_joint_id
    def test_02_group_by_joint_id(self):
        """Test routine group_by_joint_id"""
        self.grouped = readfile.group_by_joint_id(
            self.read_file, self.joint_id)
        self.assertTrue(self.grouped is not None)
        self.assertIsInstance(self.grouped, pd.core.groupby.DataFrameGroupBy)
        print("ReadFileTest:test_02_group_by_joint_id")

    # test routine split_in_objs_evnts
    def test_03_split_in_objs_evnts(self):
        """Test routine split_in_objs_evnts"""
        dict_ = readfile.split_in_objs_evnts(self.joint_id, self.grouped)
        self.assertTrue(dict_ is not None)
        for key in dict_:
            print("key: %s , value: %s" % (key, dict_[key]))
        print("ReadFileTest:test_03_split_in_objs_evnts")


if __name__ == '__main__':
    unittest.main()
