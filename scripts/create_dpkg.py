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
import biotracks.names as names
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
        sys.exit('ERROR: configuration file "%s" not found' % args.config)
    conf = configparser.ConfigParser()
    conf.read(args.config)

    top_level_dict = conf['TOP_LEVEL_INFO']
    track_dict = conf['TRACKING_DATA']
    joint_id = track_dict.get(names.OBJECT_NAME)
    link_id = track_dict.get(names.LINK_NAME)

    # read file - returns a dictionary with objects and links
    dict_ = readfile.read_file(
        args.track_fn, track_dict, log_level=args.log_level
    )
    # make directory for the csv and the dp representation
    directory = args.out_dir
    if not os.path.exists(directory):
        os.makedirs(directory)
    # write the dataframes to csv
    for k, v in dict_.items():
        v.to_csv(directory + os.sep + k + '.csv',
                 index=False, quoting=csv.QUOTE_NONE)
    logger.info('tabular files written to "%s"', directory)
    dp = createdp.create_dpkg(top_level_dict, dict_, directory, joint_id)
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

    x = track_dict.get(names.X_COORD_NAME)
    y = track_dict.get(names.Y_COORD_NAME)
    frame = track_dict.get(names.FRAME_NAME)
    # basic visualizations
    try:
        plot.prepareforplot(objects_links_tracks, x, y, frame)
        cum_df = plot.cum_displ(objects_links_tracks, link_id, x, y)
        plot.plotXY(cum_df, 'TRACK_ID', x + 'cum', y + 'cum')

        plot.plotXY(
            cum_df[cum_df['LINK_ID'] == 0], 'TRACK_ID', x + 'cum', y + 'cum'
        )
        plot.plotXY(objects_links_tracks, 'TRACK_ID', x, y)
        plot.plotXY(objects_links_tracks, 'LINK_ID', x, y)
        logger.info(
            'normalizing dataset to the origin of the coordinate system...'
        )
        norm = plot.normalize(objects_links_tracks, 'TRACK_ID', x, y)
        plot.plotXY(norm, 'TRACK_ID', x + 'norm', y + 'norm')
        plot.plotXY(norm, 'LINK_ID', x + 'norm', y + 'norm')
        logger.info('computing turning angles...')
        ta_norm = plot.compute_ta(norm, 'TRACK_ID', x, y)
        theta = ta_norm.ta[~np.isnan(ta_norm.ta)]
        theta = pd.DataFrame(theta)
        plot.plot_polar(theta, 10)
    except KeyError:
        logger.error('one or more variable provided are not in the dataset')


if __name__ == "__main__":
    main(sys.argv)
