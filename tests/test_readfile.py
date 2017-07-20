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

import pandas as pd
import pytest

from biotracks import readfile, cmso, config
from .common import EXAMPLES_DIR, RELPATHS, get_obj_dict, get_link_dict


@pytest.fixture()
def data():
    def make_data(fmt):
        base_dir = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1])
        in_fn = os.path.join(base_dir, RELPATHS[fmt][-1])
        conf_fn = os.path.join(base_dir, config.RELPATH)
        conf = config.get_conf(conf_fn=conf_fn)
        reader = readfile.TracksReader(in_fn, conf=conf)
        d = {'reader': reader}
        for k in 'objects', 'links':
            d['%s_path' % k] = os.path.join(base_dir, 'dp', '%s.csv' % k)
        dp_path = os.path.join(base_dir, 'dp', 'dp.json')
        d['bt_reader'] = readfile.BiotracksReader(dp_path, conf=conf)
        return d
    return make_data


class TestReadFile(object):

    def test_icy(self, data):
        self.__check_dicts(data('ICY'))

    def test_cellmia(self, data):
        self.__check_dicts(data('CELLMIA'))

    def test_cellprofiler(self, data):
        self.__check_dicts(data('CellProfiler'))

    def test_trackmate(self, data):
        d = data('TrackMate')
        self.__check_dicts(d)
        top_level = d['reader'].conf[config.TOP_LEVEL]
        from_source = {}
        for k in cmso.SPACE_UNIT, cmso.TIME_UNIT:
            assert k in top_level
            from_source[k] = top_level[k]
        # check override
        spatial_unit = from_source[cmso.SPACE_UNIT] + "_"
        top_level[cmso.SPACE_UNIT] = spatial_unit
        d['reader'].read()
        assert top_level[cmso.SPACE_UNIT] == spatial_unit

    def __check_dicts(self, d):
        for reader in (d['reader'], d['bt_reader']):
            for name in 'objects', 'links':
                assert type(getattr(reader, name) is pd.DataFrame)
            obj_id, link_id = cmso.OBJECT_ID, cmso.LINK_ID
            exp_link_dict = get_link_dict(
                pd.read_csv(d['links_path']), obj_id, link_id
            )
            link_dict = get_link_dict(reader.links, obj_id, link_id)
            assert link_dict == exp_link_dict
            exp_obj_dict = get_obj_dict(pd.read_csv(d['objects_path']), obj_id)
            obj_dict = get_obj_dict(reader.objects, obj_id)
            assert obj_dict.keys() == exp_obj_dict.keys()
            for k, v in exp_obj_dict.items():
                assert obj_dict[k] == pytest.approx(v)
