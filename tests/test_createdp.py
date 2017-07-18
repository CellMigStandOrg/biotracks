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

import datapackage
import pytest

from biotracks import createdp, readfile, config
from .common import EXAMPLES_DIR, RELPATHS


@pytest.fixture()
def data(tmpdir):
    def make_data(fmt):
        base_dir = os.path.join(EXAMPLES_DIR, fmt, *RELPATHS[fmt][:-1])
        exp_dp_dir = os.path.join(base_dir, 'dp')
        dp_fn = os.path.join(exp_dp_dir, 'dp.json')
        dp = datapackage.DataPackage(dp_fn)
        in_fn = os.path.join(base_dir, RELPATHS[fmt][-1])
        conf_fn = os.path.join(base_dir, config.RELPATH)
        conf = config.get_conf(conf_fn=conf_fn)
        reader = readfile.TracksReader(in_fn, conf=conf)
        reader.read()
        return {'reader': reader, 'dp': dp, 'dp_dir': str(tmpdir)}
    yield make_data
    tmpdir.remove(rec=True)


class TestCreatedp(object):

    def test_icy(self, data):
        self.__check_dps(data('ICY'))

    def test_cellmia(self, data):
        self.__check_dps(data('CELLMIA'))

    def test_cellprofiler(self, data):
        self.__check_dps(data('CellProfiler'))

    def test_trackmate(self, data):
        self.__check_dps(data('TrackMate'))

    def __check_dps(self, d):
        dp = createdp.create(d['reader'], d['dp_dir'])
        assert dp.to_dict() == d['dp'].to_dict()
        d['reader'].conf[config.TOP_LEVEL]['name'] = 'CMSO_TRACKS'
        with pytest.raises(ValueError):
            createdp.create(d['reader'], d['dp_dir'])
