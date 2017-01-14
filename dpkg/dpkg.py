import sys
import os
import collections
import configuration
import math
import pandas as pd
import numpy as np
from configuration import readConfigFile
import readfile
import createdp
import pushtopandas
import plot


# global variable - file name from the command line
# filename = r'C:\Users\paola\Desktop\cell_track\tracks_ctr.csv'
filename = sys.argv[1]
nrows = 10

# read the file given through command line
f = readfile.import_file(filename, nrows)


def lookAndReadConfigFile(track_file):
    """Looks for configuration file in the directory of f and tries to read it.

    Keyword arguments:
    track_file -- the tracking file associated with the .ini
    """
    for file_ in os.listdir(os.path.dirname(track_file)):
        if file_.endswith(".ini"):
            print('Configuration file found: {}'.format(file_))
            file_ = os.path.join(os.path.dirname(track_file), file_)
            config_dict = readConfigFile.readconfigfile(file_)
            print('Configuration dictionary: {}.'.format(config_dict))
            break
    return config_dict

config_dict = lookAndReadConfigFile(f)

track_dict = config_dict.get('TRACKING_DATA')
top_level_dict = config_dict.get('TOP_LEVEL_INFO')
joint_identifier = track_dict.get('joint_identifier')

G = readfile.group_by_joint_id(f, joint_identifier)

if G:
    D = readfile.split_in_objs_evnts(joint_identifier, G)
    # make directory for the csv and the dp representation
    wd = os.path.dirname(os.path.realpath(f))
    directory = wd + os.sep + 'dp'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # write the dataframes to csv
    for k, v in D.items():
        v.to_csv(directory + os.sep + k + '.csv', index=False)
    print(">>> csv objects and events files written to directory.")

    # the data package representation
    dp = createdp.create_dpkg(top_level_dict, D, directory, joint_identifier)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('The json: {}'.format(dp.to_json()))

    # write the dp.json to file
    with open(directory + os.sep + 'dp.json', 'w') as f_json:
        f_json.write(dp.to_json())
    print(">>> json file written to directory.")

    # push to pandas
    trajectories_df = pushtopandas.push_to_pandas(directory, joint_identifier)
    print(trajectories_df.head()), print(trajectories_df.tail())
    print('Number of rows: {}'.format(trajectories_df.shape[0]))
    print('Number of columns: {}'.format(trajectories_df.shape[1]))

    x = track_dict.get('x_coord_field')
    y = track_dict.get('y_coord_field')
    t = track_dict.get('time_field')
    # basic visualizations
    try:
        plot.prepareforplot(trajectories_df, x, y, t)
        plot.plotXY(trajectories_df, joint_identifier, x, y)

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
