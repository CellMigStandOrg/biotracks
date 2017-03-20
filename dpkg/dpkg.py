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
    for file_ in os.listdir(os.path.dirname(f)):
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

# the data package representation
dp = createdp.create_dpkg(top_level_dict, dict_, directory, joint_id)
print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
print('The json: {}'.format(dp.to_json()))

# write the dp.json to file
with open(directory + os.sep + 'dp.json', 'w') as f_json:
    f_json.write(dp.to_json())
print(">>> json file written to directory")


results_dict = pushtopandas.push_to_pandas(directory)
# global aggregation of objects and links for further analytics
aggregation = pd.merge(results_dict('links'), results_dict('objects'), how='outer', on=joint_id)
# might add aggregation of tracks as well for further analytics


# push to pandas
trajectories_df = pushtopandas.push_to_pandas(directory)
print(trajectories_df.head()), print(trajectories_df.tail())
print('Number of rows: {}'.format(trajectories_df.shape[0]))
print('Number of columns: {}'.format(trajectories_df.shape[1]))

x = track_dict.get('x_coord:CMSO')
y = track_dict.get('y_coord:CMSO')
t = track_dict.get('frame:CMSO')
# basic visualizations
try:
    plot.prepareforplot(trajectories_df, x, y, t)
    plot.plotXY(trajectories_df, joint_id, x, y)

    print('Please wait, normalizing dataset....')
    norm = plot.normalize(trajectories_df, joint_identifier, x, y)

    print('Dataset normaized to the origin of the coordinate system.')
    plot.plotXY(norm, joint_identifier, x + 'norm', y + 'norm')
    print('Please wait, computing turning angles ....')
    ta_norm = plot.compute_ta(norm, joint_identifier, x, y)
    theta = ta_norm.ta[~np.isnan(ta_norm.ta)]
    theta_deg = theta.apply(math.degrees)
    theta = pd.DataFrame(theta)
    plot.plot_polar(theta, 10)
except KeyError as ke:
    print('!!! Seems like one or more variable provided are not in the dataset.')
    print('Try again, please.')  # for now, just restart
