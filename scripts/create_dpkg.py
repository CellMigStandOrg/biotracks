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

"""\
Convert a tracking software output file to a datapackage representation.
"""

import csv
import os
import sys
import json
import configparser
import argparse

import numpy as np
import pandas as pd

import biotracks.createdp as createdp
import biotracks.plot as plot
import biotracks.pushtopandas as pushtopandas
import biotracks.readfile as readfile
import biotracks.cmso as cmso
from biotracks.utils import get_log_level, get_logger


DEFAULT_CONFIG_BASENAME = 'biotracks.ini'
DEFAULT_OUTPUT_BASENAME = 'dp'


def to_json(dp):
    return json.dumps(dp.to_dict(), indent=4, sort_keys=True)


def log_level(s):
    try:
        return get_log_level(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(e.message)


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('track_fn', metavar="TRACKING_FILE")
    parser.add_argument("-c", "--config", metavar="FILE", help="config file")
    parser.add_argument("-o", "--out-dir", metavar="DIR", help="output dir")
    parser.add_argument('--log-level', metavar='LEVEL', type=log_level,
                        default='INFO', help='logging level')
    return parser


def main(argv):
    parser = make_parser()
    args = parser.parse_args(argv[1:])
    logger = get_logger('create_dpkg', level=args.log_level, f=sys.stdout)
    input_dir = os.path.dirname(os.path.abspath(args.track_fn))
    if args.out_dir is None:
        args.out_dir = DEFAULT_OUTPUT_BASENAME
    if not args.config:
        args.config = os.path.join(input_dir, DEFAULT_CONFIG_BASENAME)
        logger.info('Trying default config file location: "%s"', args.config)
    if not os.path.isfile(args.config):
        logger.info('Config file not present, using defaults')
        conf = {'TOP_LEVEL_INFO': {'name': cmso.PACKAGE}, 'TRACKING_DATA': {}}
    else:
        conf = configparser.ConfigParser()
        conf.read(args.config)

    joint_id = cmso.OBJECT_ID
    link_id = cmso.LINK_ID
    track_id = cmso.TRACK_ID

    # read input file
    reader = readfile.TracksReader(
        args.track_fn, conf=conf, log_level=args.log_level
    )
    reader.read()
    dict_ = {'objects': reader.objects, 'links': reader.links}
    # make directory for the csv and the dp representation
    directory = args.out_dir
    if not os.path.exists(directory):
        os.makedirs(directory)
    # write the dataframes to csv
    for k, v in dict_.items():
        v.to_csv(directory + os.sep + k + '.csv',
                 index=False, quoting=csv.QUOTE_NONE)
    logger.info('tabular files written to "%s"', directory)
    dp = createdp.create_dpkg(
        conf['TOP_LEVEL_INFO'], dict_, directory, joint_id
    )
    # write the data package representation
    with open(directory + os.sep + 'dp.json', 'w') as f_json:
        f_json.write(to_json(dp) + '\n')
    logger.info('json file written to "%s"', directory)

    # push to pandas
    results_dict = pushtopandas.push_to_pandas(
        directory, joint_id, log_level=args.log_level
    )
    logger.debug('Datapackage pushed to pandas')

    objects = results_dict['objects']
    links = results_dict['links']
    tracks = results_dict['tracks']

    logger.debug('Number of rows: %d', objects.shape[0])
    logger.debug('Number of columns: %d', objects.shape[1])

    # aggregation of objects and links for further analytics
    objects_links = pd.merge(links, objects, how='outer', on=joint_id)
    # aggregation of tracks as well for further analytics
    objects_links_tracks = pd.merge(
        objects_links, tracks, how='outer', on=link_id
    )

    x = cmso.X_COORD
    y = cmso.Y_COORD
    frame = cmso.FRAME_ID
    # basic visualizations
    objects_links_tracks.sort_values(frame, axis=0, inplace=True)
    cum_df = plot.compute_cumulative_displacements(
        objects_links_tracks, link_id, x, y
    )
    plot.plotXY(cum_df, track_id, 'x_cum', 'y_cum')

    plot.plotXY(cum_df[cum_df[link_id] == 0], track_id, 'x_cum', 'y_cum')
    plot.plotXY(objects_links_tracks, track_id, x, y)
    plot.plotXY(objects_links_tracks, link_id, x, y)
    logger.info(
            'normalizing dataset to the origin of the coordinate system...'
        )
    norm = plot.normalize(objects_links_tracks, track_id, x, y)
    plot.plotXY(norm, track_id, 'x_norm', 'y_norm')
    plot.plotXY(norm, link_id, 'x_norm', 'y_norm')
    logger.info('computing displacements in the two directions of motion...')
    norm = plot.compute_displacements(norm, track_id, x, y)
    logger.info('computing turning angles...')
    norm = plot.compute_turning_angle(norm, track_id)
    theta = pd.DataFrame(norm.ta[~np.isnan(norm.ta)])
    plot.plot_polar(theta, 10)


if __name__ == "__main__":
    main(sys.argv)
