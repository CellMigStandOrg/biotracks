from dpkg.configuration import readConfigFile
import unittest
import os


class ReadConfigFileTest(unittest.TestCase):
    """Read a configuration file test."""

    # preparing to test
    def setUp(self):
        """ Setting up for the test """
        print("ReadConfigFileTest:setUp_:begin")
        global cf
        cf = "test_files/cell_track_dpkg.ini"
        print(cf)
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
        dict_ = readConfigFile.readconfigfile(cf)
        print('Dictionary returned: {}'.format(dict_))
        assert dict_ is not None
