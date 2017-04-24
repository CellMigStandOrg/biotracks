import csv
import math
import os
import sys
import json

import numpy as np
import pandas as pd

import dpkg.createdp as createdp
import dpkg.plot as plot
import dpkg.pushtopandas as pushtopandas
import dpkg.readfile as readfile
import dpkg.names as names
from dpkg.configuration import readConfigFile

# global variable - file name from the command line
f = sys.argv[1]


def to_json(dp):
    return json.dumps(dp.to_dict(), indent=4, sort_keys=True)


def lookAndReadConfigFile():
    """Looks for configuration file and tries to read it.
    """
    for file_ in os.listdir(os.path.dirname(os.path.abspath(f))):
        if file_.endswith(".ini"):
            print('Configuration file found: {}'.format(file_))
            config_dict = readConfigFile.readconfigfile(os.path.join(os.path.dirname(f), file_))
            print('Configuration dictionary: {}.'.format(config_dict))
            break
    return config_dict

config_dict = lookAndReadConfigFile()
top_level_dict = config_dict.get('TOP_LEVEL_INFO')
track_dict = config_dict.get('TRACKING_DATA')
joint_id = track_dict.get(names.OBJECT_NAME)
link_id = track_dict.get(names.LINK_NAME)

# read file - returns a dictionary with objects and links
dict_ = readfile.read_file(f, track_dict)
# make directory for the csv and the dp representation
wd = os.path.dirname(os.path.realpath(f))
directory = wd + os.sep + 'dp'
if not os.path.exists(directory):
    os.makedirs(directory)
# write the dataframes to csv
for k, v in dict_.items():
    v.to_csv(directory + os.sep + k + '.csv',
             index=False, quoting=csv.QUOTE_NONE)
print(">>> tabular objects and links written to csv files in the dp folder")

# the data package representation
dp = createdp.create_dpkg(top_level_dict, dict_, directory, joint_id)
print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
print('The json: {}'.format(dp.to_json()))

# write the dp.json to file
with open(directory + os.sep + 'dp.json', 'w') as f_json:
    f_json.write(to_json(dp) + '\n')
print(">>> json file written to directory")

# push to pandas
results_dict = pushtopandas.push_to_pandas(directory, joint_id)
print('Datapackage pushed to pandas.')

objects = results_dict['objects']
links = results_dict['links']
tracks = results_dict['tracks']

print('Number of rows: {}'.format(objects.shape[0]))
print('Number of columns: {}'.format(objects.shape[1]))

# aggregation of objects and links for further analytics
objects_links = pd.merge(links, objects, how='outer', on=joint_id)
# aggregation of tracks as well for further analytics
objects_links_tracks = pd.merge(objects_links, tracks, how='outer', on=link_id)

x = track_dict.get(names.X_COORD_NAME)
y = track_dict.get(names.Y_COORD_NAME)
frame = track_dict.get(names.FRAME_NAME)
# basic visualizations
try:
    plot.prepareforplot(objects_links_tracks, x, y, frame)
    cum_df = plot.cum_displ(objects_links_tracks, link_id, x, y)
    plot.plotXY(cum_df, 'TRACK_ID', x + 'cum', y + 'cum')

    plot.plotXY(cum_df[cum_df['LINK_ID'] == 0], 'TRACK_ID', x + 'cum', y + 'cum')
    plot.plotXY(objects_links_tracks, 'TRACK_ID', x, y)

    print('Please wait, normalizing dataset....')
    norm = plot.normalize(objects_links_tracks, 'TRACK_ID', x, y)

    print('Dataset normaized to the origin of the coordinate system.')
    plot.plotXY(norm, 'TRACK_ID', x + 'norm', y + 'norm')
    print('Please wait, computing turning angles ....')
    ta_norm = plot.compute_ta(norm, 'TRACK_ID', x, y)
    theta = ta_norm.ta[~np.isnan(ta_norm.ta)]
    theta_deg = theta.apply(math.degrees)
    theta = pd.DataFrame(theta)
    plot.plot_polar(theta, 10)
except KeyError as ke:
    print('!!! Seems like one or more variable provided are not in the dataset.')
    print('Try again, please.')  # for now, just restart
