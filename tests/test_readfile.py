import os

from biotracks import readfile
from pytest import fixture
import pandas as pd


class Data(object):

    def __init__(self):
        self.read_file = None
        directory = os.path.dirname(__file__)
        self.f = os.path.join(directory, "test_files", "test_fake_tracks_tm.xml")


@fixture(scope="class")
def data():
    return Data()


class TestReadFile(object):

    def test_01_import_file(self, data):
        exp_keys = set(['objects', 'links'])
        assert os.path.exists(data.f)
        data.read_file = readfile.read_file(data.f, {})
        assert data.read_file is not None
        assert set(data.read_file) == exp_keys
        for k in exp_keys:
            assert type(data.read_file[k]) is pd.DataFrame
