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


def get_obj_dict(df, obj_id):
    d = {}
    for _, series in df.iterrows():
        k = series.pop(obj_id)
        assert k not in d
        d[k] = series.to_dict()
    return d


def get_link_dict(df, obj_id, link_id):
    d = {}
    for _, series in df.iterrows():
        d.setdefault(series[link_id], set()).add(series[obj_id])
    return d


def get_track_dict(df, link_id, track_id):
    return get_link_dict(df, link_id, track_id)  # same logic


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(THIS_DIR, os.pardir, 'examples')
RELPATHS = {
    'ICY': ['example_2', 'track_processor_ICY.xls'],
    'CELLMIA': ['example_1', '0001_mode1_z000_f000_tracking.txt'],
    'TrackMate': ['example_1', 'FakeTracks.xml'],
    'CellProfiler': ['example_1', 'output', 'bloboverlap15_spots.csv'],
}
