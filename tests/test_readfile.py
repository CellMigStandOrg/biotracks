import os

from biotracks import readfile
from pytest import fixture
import pandas as pd


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, 'test_files')
EXP_KEYS = frozenset(['objects', 'links'])


@fixture()
def data():
    def make_data(basename):
        in_fn = os.path.join(DATA_DIR, basename)
        d = readfile.read_file(in_fn, {})
        assert set(d) == EXP_KEYS
        for k in EXP_KEYS:
            assert type(d[k]) is pd.DataFrame
        return d
    return make_data


class TestReadFile(object):

    def test_trackmate(self, data):
        d = data('test_fake_tracks_tm.xml')
        assert list(d['objects']) == [
            'SPOT_ID', 'FRAME', 'POSITION_X', 'POSITION_Y'
        ]
        assert list(d['links']) == ['LINK_ID', 'SPOT_ID']
