from biotracks.configuration import readConfigFile
from pytest import fixture
import os


@fixture()
def ini_file():
    directory = os.path.dirname(__file__)
    return os.path.join(
        directory, "test_files", "biotracks.ini")


class TestReadConfigFile(object):
    """Read a configuration file test."""

    def test_01_readconfigfile(self, ini_file):
        """Test routine readconfigfile"""
        print("ReadConfigFileTest:test_01_readconfigfile")
        assert os.path.exists(ini_file)
        dict_ = readConfigFile.readconfigfile(ini_file)
        print('Dictionary returned: {}'.format(dict_))
        assert dict_ is not None
