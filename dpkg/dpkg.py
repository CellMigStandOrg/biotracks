import sys
import os
import collections
import configuration
import readfile
import createdp
import pushtopandas
import plot
import math
import pandas as pd
import numpy as np

# global variable - file name from the command line
filename = r'C:\Users\paola\Desktop\cell_track\tracks_ctr.csv'
# filename = sys.argv[1]
nrows = 10


def getinputfromuser():
    x_coord = input(
        "Please enter the column name for the x_coordinate: ")
    print('>>> x_coord is {}'.format(x_coord))

    y_coord = input(
        "Please enter the column name for the y_coordinate: ")
    print('>>> y_coord is {}'.format(y_coord))

    time = input(
        "Please enter the column name for the time: ")
    print('>>> time is {}'.format(time))

    return (x_coord, y_coord, time)

# read the file given through command line
f = readfile.import_file(filename, nrows)
# search for correspondent .ini configuration file in the directory
# if the file is found, read it and get the properties dictionary
for file_ in os.listdir(f):
    if file_.endswith(".ini"):
        print(file_)
        config_file = file_
        break


joint_identifier = input(
    "Please enter the column name for the joint_identifier: ")
print('>>> joint_identifier is {}'.format(joint_identifier))

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
    dp = createdp.create_dpkg(D, directory, joint_identifier)
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

    # basic visualizations
    input_reference = getinputfromuser()
    print('The input reference was: {}'.format(input_reference))
    try:
        plot.prepareforplot(trajectories_df, input_reference[
                            0], input_reference[1], input_reference[2])
        plot.plotXY(trajectories_df, joint_identifier, input_reference[
            0], input_reference[1])

        print('Please wait, normalizing dataset....')
        norm = plot.normalize(trajectories_df, joint_identifier, input_reference[
            0], input_reference[1])

        print('Dataset normaized to the origin of the coordinate system.')
        plot.plotXY(norm, joint_identifier, input_reference[
            0] + 'norm', input_reference[
                1] + 'norm')
        print('Please wait, computing turning angles ....')
        ta_norm = plot.compute_ta(norm, joint_identifier, input_reference[
            0], input_reference[1])
        theta = ta_norm.ta[~np.isnan(ta_norm.ta)]
        theta_deg = theta.apply(math.degrees)
        theta = pd.DataFrame(theta)
        plot.plot_polar(theta, 10)
    except KeyError as ke:
        print('!!! Seems like one or more variable provided are not in the dataset.')
        print('Try again, please.')  # for now, just restart
