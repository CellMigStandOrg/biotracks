# -*- coding: utf-8 -*-
import os
import sys
# needed if *not* using nosetests
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dpkg")
import dpkg
from dpkg import readfile
import unittest
import pandas as pd

directory = r'C:\Users\paola\Desktop\cell_track'


class ReadFileTest(unittest.TestCase):
    """Read file test."""

    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        print("ReadFileTest:setUp_:begin")
        global f
        global n
        global joint_id
        f = os.path.join(directory, "tracks_ctr.csv")
        n = 20
        joint_id = 'Track N'
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
        self.assertTrue(os.path.exists(f))
        global read_file
        read_file = readfile.import_file(f, n)
        print(read_file)
        assert read_file is not None

    # test routine group_by_joint_id
    def test_02_group_by_joint_id(self):
        """Test routine group_by_joint_id"""
        global grouped
        grouped = readfile.group_by_joint_id(read_file, joint_id)
        self.assertTrue(grouped is not None)
        self.assertIsInstance(grouped, pd.core.groupby.DataFrameGroupBy)
        print("ReadFileTest:test_02_group_by_joint_id")

    # test routine split_in_objs_evnts
    def test_03_split_in_objs_evnts(self):
        """Test routine split_in_objs_evnts"""
        dict_ = readfile.split_in_objs_evnts(joint_id, grouped)
        self.assertTrue(dict_ is not None)
        for key in dict_:
            print("key: %s , value: %s" % (key, dict_[key]))
        print("ReadFileTest:test_03_split_in_objs_evnts")


if __name__ == '__main__':
    unittest.main()
