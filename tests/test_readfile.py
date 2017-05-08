import os
import configparser

import pandas as pd
import pytest

from biotracks import readfile, names


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(THIS_DIR, os.pardir, 'examples')
RELPATHS = {
    'ICY': ['example_1', 'track_processor_ICY.xls'],
    'TrackMate': ['example_1', 'FakeTracks.xml'],
    'CellProfiler': ['example_1', 'output', 'bloboverlap15_spots.csv'],
}
EXP_KEYS = frozenset(['objects', 'links'])


@pytest.fixture()
def data():
    def make_data(fmt):
        in_fn = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt])
        conf_fn = os.path.join(
            EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1], "biotracks.ini"
        )
        conf = configparser.ConfigParser()
        conf.read(conf_fn)
        d = readfile.read_file(in_fn, conf['TRACKING_DATA'])
        assert set(d) == EXP_KEYS
        for k in EXP_KEYS:
            assert type(d[k]) is pd.DataFrame
        return d, conf
    return make_data


class TestReadFile(object):

    @pytest.mark.skip(reason="reader currently slow and overwrites repo files")
    def test_icy(self, data):
        d, _ = data('ICY')
        assert list(d['objects']) == ['OBJECT_ID', 't', 'x', 'y', 'z']
        assert list(d['links']) == ['LINK_ID', 'OBJECT_ID']

    def test_cellprofiler(self, data):
        d, conf = data('CellProfiler')
        td = conf['TRACKING_DATA']
        assert list(d['objects']) == [
            td[names.OBJECT_NAME],
            td[names.FRAME_NAME],
            td[names.X_COORD_NAME],
            td[names.Y_COORD_NAME],
        ]
        assert list(d['links']) == [td[names.LINK_NAME], td[names.OBJECT_NAME]]

    def test_trackmate(self, data):
        d, _ = data('TrackMate')
        assert list(d['objects']) == [
            'SPOT_ID', 'FRAME', 'POSITION_X', 'POSITION_Y'
        ]
        assert list(d['links']) == ['LINK_ID', 'SPOT_ID']
