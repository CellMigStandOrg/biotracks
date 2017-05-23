# #%L
# Copyright (c) 2016-2017 Cell Migration Standardisation Organization
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%

import os
import configparser

import pandas as pd
import pytest

from biotracks import names
from biotracks.pushtopandas import push_to_pandas
from .common import (
    EXAMPLES_DIR, RELPATHS, get_obj_dict, get_link_dict, get_track_dict
)


@pytest.fixture()
def data():
    def make_data(fmt):
        base_dir = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1])
        dp_dir = os.path.join(base_dir, 'dp')
        d = {'dp_dir': dp_dir}
        d['obj_df'] = pd.read_csv(os.path.join(dp_dir, 'objects.csv'))
        d['links_df'] = pd.read_csv(os.path.join(dp_dir, 'links.csv'))
        d['tracks_df'] = pd.read_csv(os.path.join(dp_dir, 'tracks.csv'))
        conf_fn = os.path.join(base_dir, 'biotracks.ini')
        conf = configparser.ConfigParser()
        conf.read(conf_fn)
        d['conf'] = conf
        return d
    return make_data


class TestPushToPandas(object):

    def test_icy(self, data):
        d = data('ICY')
        self.__check_dicts(d, 'OBJECT_ID', 'LINK_ID', 'TRACK_ID')

    def test_cellprofiler(self, data):
        d = data('CellProfiler')
        td = d['conf']['TRACKING_DATA']
        self.__check_dicts(
            # TODO: add a track name slot to names.py and the config file spec
            d, td[names.OBJECT_NAME], td[names.LINK_NAME], 'TRACK_ID'
        )

    def test_trackmate(self, data):
        d = data('TrackMate')
        self.__check_dicts(d, 'SPOT_ID', 'LINK_ID', 'TRACK_ID')

    def __check_dicts(self, d, obj_id, link_id, track_id):
        ret = push_to_pandas(d['dp_dir'], obj_id)
        exp_track_dict = get_track_dict(d['tracks_df'], link_id, track_id)
        track_dict = get_track_dict(ret['tracks'], link_id, track_id)
        assert track_dict == exp_track_dict
        exp_link_dict = get_link_dict(d['links_df'], obj_id, link_id)
        link_dict = get_link_dict(ret['links'], obj_id, link_id)
        assert link_dict == exp_link_dict
        exp_obj_dict = get_obj_dict(d['obj_df'], obj_id)
        obj_dict = get_obj_dict(ret['objects'], obj_id)
        assert obj_dict.keys() == exp_obj_dict.keys()
        for k, v in exp_obj_dict.items():
            assert obj_dict[k] == pytest.approx(v)
