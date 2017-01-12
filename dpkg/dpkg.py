# global variable - file name from the command line
import sys
import os

filename = sys.argv[1]
nrows = 10


import readfile

f = readfile.import_file(filename, nrows)
joint_id = input("Please enter the column name for the joint_identifier: ")
print('>>> joint_identifier is {}'.format(joint_id))

G = readfile.group_by_joint_id(f, joint_id)

if G != None:
    D = readfile.split_in_objs_evnts(joint_id, G)
    # make directory for the csv and the dp representation
    wd = os.path.dirname(os.path.realpath(f))
    directory = wd + os.sep + 'dp'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # write the dataframes to csv
    for k, v in D.items():
        v.to_csv(directory + os.sep + k + '.csv', index=False)
    print(">>> csv objects and events files written to directory!")
