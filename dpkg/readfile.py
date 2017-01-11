# import needed libraries
import sys
import io
import os
import csv
import pandas as pd

# global variable - file name from the command line
filename = sys.argv[1]
nrows = 10


def xls_to_csv(xls_file):
    """Utility function needed to read Excel files."""

    import xlrd
    from xlrd import XLRDError

    x = xlrd.open_workbook(xls_file)
    x1 = x.sheet_by_index(0)
    name, extension = os.path.splitext(xls_file)
    csvfile = open(name + '.csv', 'wb')
    writecsv = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

    for rownum in xrange(sh.nrows):
        writecsv.writerow(x1.row_values(rownum))

    csvfile.close()


def trackMate_to_csv(trackMate_file):
    """Utility function to read a TrackMate XML file and convert it to a plain csv."""

    import xml.etree.ElementTree as ET
    tree = ET.parse(trackMate_file)
    root = tree.getroot()
    print('>>>')
    print('Reading a TrackMate XML file version {}'.format(
        root.attrib.get('version')))

    # dictionary for the spots
    spots_dict = {}
    for child in root.find('Model'):
        if child.tag == 'AllSpots':
            spots = child
            for spot_in_frame in spots.getchildren():
                for spot in spot_in_frame.getchildren():
                    spot_id = int(spot.get('ID'))

                    position_x = float(spot.get('POSITION_X'))
                    position_y = float(spot.get('POSITION_Y'))
                    position_t = float(spot.get('POSITION_T'))

                    spots_dict[spot_id] = (position_x, position_y, position_t)

    print('>>> Found {} unique spots'.format(len(spots_dict)))

    # dictionary for the tracks
    tracks_dict = {}
    for child in root.find('Model'):
        if child.tag == 'AllTracks':
            tracks = child
            for track in tracks.getchildren():
                track_index = int(track.get('TRACK_INDEX'))
                tracks_dict[track_index] = []
                for edge in track.getchildren():
                    spot_source_id = int(edge.get('SPOT_SOURCE_ID'))
                    spot_target_id = int(edge.get('SPOT_TARGET_ID'))

                    tracks_dict[track_index].append(
                        spots_dict.get(spot_source_id))
                    tracks_dict[track_index].append(
                        spots_dict.get(spot_target_id))

    print('>>> Found {} unique tracks'.format(len(tracks_dict)))

    # write the dictionary to file
    name, extension = os.path.splitext(trackMate_file)
    csvfile = open(name + '.csv', 'w')
    writecsv = csv.writer(csvfile, lineterminator='\n')
    # write header
    writecsv.writerow(["trackID", "x", "y", "t"])

    for key, value in tracks_dict.items():
        for element in tracks_dict.get(key):
            row = [key, element[0], element[1], element[2]]
            writecsv.writerow(row)

    csvfile.close()


def import_file(f, n):
    """Takes file from command line and # of rows to visualize.

    Keyword arguments:
    f -- the file (from command line)
    n -- number of rows to visualize (default 10)
    """
    if f.endswith('.xls'):
        try:
            xls_to_csv(f)
        except XLRDError:
            # copy the file and save it as csv
            import shutil
            name, extension = os.path.splitext(f)
            shutil.copyfile(f, name + '.csv')
            f = name + '.csv'
            print('Not an excel file.' + ' Copied and simply renamed to csv.')

    elif f.endswith('.xml'):
        trackMate_to_csv(f)
        name, extension = os.path.splitext(f)
        f = name + '.csv'

    # open the file and show a quick preview
    print('>>> opening file: %s' % f)
    with open(f, 'r') as reader:
        for i in range(n):
            if i == 0:
                print('>>> header of the file:')
            elif i == 1:
                print('>>> rest of the file:')
            print(reader.readline())  # print header
    return f


def group_by_joint_id(f, joint_id):
    """Group the tabular data by the joint_identifier.

    Keyword arguments:
    f -- the file (from command line)
    n -- the joint_identifier (from command line)
    """
    df = pd.read_table(f, sep=None, engine='python')
    # try to group by the joint_id
    try:
        grouped = df.groupby(joint_id)
        print(grouped.size()[:5])
        return grouped
    except KeyError:  # throw an error if the wrong id is passed
        print('Seems like ' + joint_id +
              " is not the right joint_identifier for " + os.path.basename(f))
        return None

# create objects and events dataframes


def split_in_objs_evnts(grouped):
    """Creta the objects and events dataframes.

    Keyword arguments:
    grouped -- the object returned by the split events
    """
    dfs = []
    for name, group in grouped:
        df = group.reset_index()
        dfs.append(df)

    objects_df = pd.concat(dfs)

    events_df = pd.DataFrame(grouped.size()).reset_index()
    events_df.columns = [joint_identifier, 'events_size']

    return {'objects': objects_df, 'events': events_df}

# the dictionary
D = split_in_objs_evnts(G)

# make directory for the csv and the dp representation
wd = os.path.dirname(os.path.realpath(f))
directory = wd + os.sep + 'dp'
if not os.path.exists(directory):
    os.makedirs(directory)

# write the dataframes to csv
for k, v in D.items():
    v.to_csv(directory + os.sep + k + '.csv', index=False)
    print(">>> Files written to directory!")
