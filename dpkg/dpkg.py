import sys
import os
import readfile
import createdp
import pushtopandas
import plot

# global variable - file name from the command line
filename = sys.argv[1]
nrows = 10


f = readfile.import_file(filename, nrows)
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
    print('number of rows {}'.format(trajectories_df.shape[0]))
    print('number of columns {}'.format(trajectories_df.shape[1]))

    # basic visualizations
    x_coord = input(
        "Please enter the column name for the x_coordinate: ")
    print('>>> x_coord is {}'.format(x_coord))

    y_coord = input(
        "Please enter the column name for the y_coordinate: ")
    print('>>> y_coord is {}'.format(y_coord))

    time = input(
        "Please enter the column name for the time: ")
    print('>>> time is {}'.format(time))

    plot.prepareforplot(trajectories_df, x_coord, y_coord, time)
    plot.plotrawtraj(trajectories_df, joint_identifier, x_coord, y_coord)
