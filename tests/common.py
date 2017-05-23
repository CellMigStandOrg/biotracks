# #%L
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
    'TrackMate': ['example_1', 'FakeTracks.xml'],
    'CellProfiler': ['example_1', 'output', 'bloboverlap15_spots.csv'],
}
