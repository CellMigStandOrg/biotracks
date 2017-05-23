# #%L
# #L%

import os
import configparser

import datapackage
import pytest

from biotracks import createdp, names
from .common import EXAMPLES_DIR, RELPATHS


@pytest.fixture()
def data():
    def make_data(fmt):
        base_dir = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1])
        dp_dir = os.path.join(base_dir, 'dp')
        dp_fn = os.path.join(dp_dir, 'dp.json')
        dp = datapackage.DataPackage(dp_fn)
        conf_fn = os.path.join(base_dir, 'biotracks.ini')
        conf = configparser.ConfigParser()
        conf.read(conf_fn)
        return {'dp': dp, 'dp_dir': dp_dir, 'conf': conf}
    return make_data


class TestCreatedp(object):

    def test_icy(self, data):
        d = data('ICY')
        self.__check_dps(d, 'OBJECT_ID')

    def test_cellprofiler(self, data):
        d = data('CellProfiler')
        self.__check_dps(d, d['conf']['TRACKING_DATA'][names.OBJECT_NAME])

    def test_trackmate(self, data):
        d = data('TrackMate')
        self.__check_dps(d, 'SPOT_ID')

    def __check_dps(self, d, obj_id):
        tld = d['conf']['TOP_LEVEL_INFO']
        dp = createdp.create_dpkg(tld, {}, d['dp_dir'], obj_id)
        assert dp.to_dict() == d['dp'].to_dict()
