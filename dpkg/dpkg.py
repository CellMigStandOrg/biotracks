import collections
import csv
import math
import os
import sys

import numpy as np
import pandas as pd

import configuration
import createdp
import plot
import pushtopandas
import readfile
from configuration import readConfigFile

# global variable - file name from the command line
f = sys.argv[1]

# read file - returns a dictionary with objects and links
dict_ = readfile.read_file(f)
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
joint_id = track_dict.get('object_id_cmso')
link_id = track_dict.get('link_id_cmso')

# the data package representation
dp = createdp.create_dpkg(top_level_dict, dict_, directory, joint_id)
print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
print('The json: {}'.format(dp.to_json()))

# write the dp.json to file
with open(directory + os.sep + 'dp.json', 'w') as f_json:
    f_json.write(dp.to_json())
print(">>> json file written to directory")

# push to pandas
results_dict = pushtopandas.push_to_pandas(directory)
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


x = track_dict.get('x_coord_cmso')
y = track_dict.get('y_coord_cmso')
frame = track_dict.get('frame_cmso')
# basic visualizations
try:
    plot.prepareforplot(objects_links_tracks, x, y, frame)
    plot.plotXY(objects_links_tracks, link_id, x, y)

    print('Please wait, normalizing dataset....')
    norm = plot.normalize(objects_links_tracks, link_id, x, y)

    print('Dataset normaized to the origin of the coordinate system.')
    plot.plotXY(norm, link_id, x + 'norm', y + 'norm')
    print('Please wait, computing turning angles ....')
    ta_norm = plot.compute_ta(norm, link_id, x, y)
    theta = ta_norm.ta[~np.isnan(ta_norm.ta)]
    theta_deg = theta.apply(math.degrees)
    theta = pd.DataFrame(theta)
    plot.plot_polar(theta, 10)
except KeyError as ke:
    print('!!! Seems like one or more variable provided are not in the dataset.')
    print('Try again, please.')  # for now, just restart
