import os
import configparser

import pandas as pd
import pytest

from biotracks import readfile, names
from .common import EXAMPLES_DIR, RELPATHS, get_obj_dict, get_link_dict


@pytest.fixture()
def data():
    def make_data(fmt):
        base_dir = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1])
        in_fn = os.path.join(base_dir, RELPATHS[fmt][-1])
        conf_fn = os.path.join(base_dir, "biotracks.ini")
        conf = configparser.ConfigParser()
        conf.read(conf_fn)
        d = readfile.read_file(in_fn, conf['TRACKING_DATA'])
        assert set(d) == set(['objects', 'links'])
        for k in list(d):
            assert type(d[k]) is pd.DataFrame
            d['%s_path' % k] = os.path.join(base_dir, 'dp', '%s.csv' % k)
        d['conf'] = conf
        return d
    return make_data


class TestReadFile(object):

    def test_icy(self, data):
        d = data('ICY')
        self.__check_dicts(d, 'OBJECT_ID', 'LINK_ID')

    def test_cellprofiler(self, data):
        d = data('CellProfiler')
        td = d['conf']['TRACKING_DATA']
        self.__check_dicts(d, td[names.OBJECT_NAME], td[names.LINK_NAME])

    def test_trackmate(self, data):
        d = data('TrackMate')
        self.__check_dicts(d, 'SPOT_ID', 'LINK_ID')

    def __check_dicts(self, d, obj_id, link_id):
        exp_link_dict = get_link_dict(
            pd.read_csv(d['links_path']), obj_id, link_id
        )
        link_dict = get_link_dict(d['links'], obj_id, link_id)
        assert link_dict == exp_link_dict
        exp_obj_dict = get_obj_dict(pd.read_csv(d['objects_path']), obj_id)
        obj_dict = get_obj_dict(d['objects'], obj_id)
        assert obj_dict.keys() == exp_obj_dict.keys()
        for k, v in exp_obj_dict.items():
            assert obj_dict[k] == pytest.approx(v)
