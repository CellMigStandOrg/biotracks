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
