import configuration
from configuration import readConfigFile
import unittest
import os

directory = r'C:\Users\paola\Desktop'


class ReadConfigFileTest(unittest.TestCase):
    """Read a configuration file test."""

    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        print("ReadConfigFileTest:setUp_:begin")
        global cf
        cf = os.path.join(directory, "cell_track_dpkg.ini")
        print("ReadConfigFileTest:setUp_:end")

    # ending the test
    def tearDown(self):
        """Cleaning up after the test"""
        print("ReadConfigFileTest:tearDown_:begin")
        # do something...
        print("ReadConfigFileTest:tearDown_:end")

    # test routine read
    def test_01_readconfigfile(self):
        """Test routine readconfigfile"""
        print("ReadConfigFileTest:test_01_readconfigfile")
        self.assertTrue(os.path.exists(cf))
        global dict_
        dict_ = readConfigFile.readconfigfile(cf)
        print('Dictionary returned: {}'.format(dict_))
        assert dict_ is not None
