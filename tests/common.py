import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(THIS_DIR, os.pardir, 'examples')
RELPATHS = {
    'ICY': ['example_1', 'track_processor_ICY.xls'],
    'TrackMate': ['example_1', 'FakeTracks.xml'],
    'CellProfiler': ['example_1', 'output', 'bloboverlap15_spots.csv'],
}
