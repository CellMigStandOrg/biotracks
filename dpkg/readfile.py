# import needed libraries
import csv
import os
import xml.etree.ElementTree as ET

import pandas as pd
import xlrd
from xlrd import XLRDError


def xls_to_csv(xls_file):
    """Utility function to read Excel files."""

    x = xlrd.open_workbook(xls_file)
    x1 = x.sheet_by_index(0)
    name, extension = os.path.splitext(xls_file)

    with open(name + '.csv', 'w', encoding='utf-8') as csv_file:
        writecsv = csv.writer(csv_file, quoting=csv.QUOTE_NONE)
        for rownum in range(x1.nrows):
            writecsv.writerow(x1.row_values(rownum))

    csv_file.close()


def trackMate_to_csv(trackMate_file):
    """Utility function to read a TrackMate XML file and convert it to a plain csv."""

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

                    SPOT_ID = int(spot.get('ID'))
                    spots_dict[SPOT_ID] = []

                    FRAME = int(spot.get('FRAME'))
                    POSITION_X = float(spot.get('POSITION_X'))
                    POSITION_Y = float(spot.get('POSITION_Y'))

                    # insert into dict {frame, x, y}
                    spots_dict[SPOT_ID].append((FRAME, POSITION_X, POSITION_Y))

    print('>>> Found {} unique spots'.format(len(spots_dict)))

    # write the objects dictionary to file
    name, extension = os.path.splitext(trackMate_file)
    objects_csvfile = open(name + '_objects.csv', 'w')
    writecsv = csv.writer(objects_csvfile, lineterminator='\n')
    # write header
    writecsv.writerow(["SPOT_ID", "FRAME", "POSITION_X", "POSITION_Y"])

    for key, value in spots_dict.items():
        for element in spots_dict.get(key):
            row = [key, element[0], element[1], element[2]]
            writecsv.writerow(row)

    objects_csvfile.close()

    # dictionary for the edges (which will be converted into CMSO:links)
    edges_dict = {}
    for child in root.find('Model'):
        if child.tag == 'AllTracks':
            tracks = child
            EDGE_ID = 0
            for track in tracks.getchildren():
                TRACK_ID = int(track.get('TRACK_ID'))
                for edge in track.getchildren():
                    EDGE_ID = EDGE_ID + 1
                    edges_dict[EDGE_ID] = []
                    SPOT_SOURCE_ID = int(edge.get('SPOT_SOURCE_ID'))
                    SPOT_TARGET_ID = int(edge.get('SPOT_TARGET_ID'))

                    SOURCE_FRAME = spots_dict.get(SPOT_SOURCE_ID)[0][0]
                    TARGET_FRAME = spots_dict.get(SPOT_TARGET_ID)[0][0]

                    edges_dict[EDGE_ID].append(TRACK_ID)
                    edges_dict[EDGE_ID].append(SPOT_SOURCE_ID)
                    edges_dict[EDGE_ID].append(SPOT_TARGET_ID)
                    edges_dict[EDGE_ID].append(SOURCE_FRAME)
                    edges_dict[EDGE_ID].append(TARGET_FRAME)

    print('>>> Found {} unique edges'.format(len(edges_dict)))

    # write the tracks dictionary to file
    edges_csvfile = open(name + '_edges.csv', 'w')
    writecsv = csv.writer(edges_csvfile, lineterminator='\n')
    # write header
    writecsv.writerow(
        ["EDGE_ID", "TRACK_ID", "SPOT_SOURCE_ID", "SPOT_TARGET_ID", "SOURCE_FRAME", "TARGET_FRAME"])

    for key, value in edges_dict.items():
        row = [key, value[0], value[1], value[2], value[3], value[4]]
        writecsv.writerow(row)

    edges_csvfile.close()

    edges_csvfile = open(name + '_edges.csv', 'r')
    edges_df = pd.read_csv(edges_csvfile)

    ordered_edges_df = edges_df.sort_values(
        ['TRACK_ID', 'SOURCE_FRAME', 'TARGET_FRAME'])
    ordered_edges_df.reset_index(inplace=True)
    print(ordered_edges_df)

    link_dict = {}

    LINK_ID = 0
    for i, row in ordered_edges_df.iterrows():
        print('i is: {}'.format(i))

        if LINK_ID not in link_dict:
            link_dict[LINK_ID] = []

        temp_row = ordered_edges_df.loc[[i]]
        if i == 0:

            # LOOK AT FRAMES

            previousSource, previousTarget = row[
                'SPOT_SOURCE_ID'], row['SPOT_TARGET_ID']
            # take both spots and assign them to the current link
            link_dict[LINK_ID].append(previousSource)
            #link_dict[LINK_ID].append(previousTarget)

            print(link_dict)
        else:
            currentSource, currentTarget = row[
                'SPOT_SOURCE_ID'], row['SPOT_TARGET_ID']
            print(link_dict)
            if currentSource == previousSource:
                # split event

                origin_link_id = LINK_ID
                LINK_ID = origin_link_id + 1

                if LINK_ID not in link_dict:
                    link_dict[LINK_ID] = []

                link_dict[origin_link_id].append(previousSource)
                link_dict[LINK_ID].append(currentSource)
                print(previousSource, currentSource)

            elif currentTarget == previousTarget:
                # merge event
                print('OK')

            else:
                # no events - good to go
                # assign objects to the link
                link_dict[LINK_ID].append(currentSource)
                #link_dict[LINK_ID].append(currentTarget)

            previousSource, previousTarget = row[
                'SPOT_SOURCE_ID'], row['SPOT_TARGET_ID']




    for track_id in edges_df.TRACK_ID.unique():
        subset_track = edges_df.loc[edges_df['TRACK_ID'] == track_id]
        subset_track.reset_index(inplace=True)
        ordered_subset_track = subset_track.sort_values(
            ['SOURCE_FRAME', 'TARGET_FRAME'])
        # print(ordered_subset_track)

        # initialize link and keep adding objects to it
        # unless

    """
    ###### STARTINT LINK######################################
    list_ = []
    #links_df = pd.DataFrame(columns=['LINK_ID','SPOT_ID'])
    link_id = -1

    for track_id in edges_df.TRACK_ID.unique():

        link_id = link_id + 1
        subset = edges_df.loc[edges_df['TRACK_ID'] == track_id]
        subset.reset_index(inplace = True)
        for index, row in subset.iterrows():

            subset_row = subset.loc[[index]]
            subset_row['LINK_ID'], subset_row[
                'SPOT_ID'] = link_id, row['SPOT_SOURCE_ID']
            list_.append(subset_row)


        index_row = subset.shape[0] - 1
        last_row = subset.loc[[index_row]]

        last_row['LINK_ID'], last_row[
            'SPOT_ID'] = link_id,  last_row['SPOT_TARGET_ID']
        list_.append(last_row)

    links_df = pd.concat(list_)
    links_df = links_df[['LINK_ID', 'SPOT_ID']]
    print(links_df)
    links_df.to_csv(name + '_links.csv', index=False)
"""

"""
    # dictionary for the tracks
    tracks_dict = {}
    for child in root.find('Model'):
        if child.tag == 'AllTracks':
            tracks = child
            for track in tracks.getchildren():
                TRACK_ID = int(track.get('TRACK_ID'))
                tracks_dict[TRACK_ID] = []
                for edge in track.getchildren():
                    SPOT_SOURCE_ID = int(edge.get('SPOT_SOURCE_ID'))
                    SPOT_TARGET_ID = int(edge.get('SPOT_TARGET_ID'))

                    tracks_dict[TRACK_ID].append(SPOT_SOURCE_ID)
                    tracks_dict[TRACK_ID].append(SPOT_TARGET_ID)

    print('>>> Found {} unique tracks'.format(len(tracks_dict)))

    # write the tracks dictionary to file
    tracks_csvfile = open(name + '_tracks.csv', 'w')
    writecsv = csv.writer(tracks_csvfile, lineterminator='\n')
    # write header
    writecsv.writerow(["TRACK_ID", "SPOT_ID"])

    for key, value in tracks_dict.items():
        for element in tracks_dict.get(key):
            row = [key]
            writecsv.writerow(row)

    tracks_csvfile.close()
"""


def clean_icy_file(icy_file):
    """Utility function to clean up a file generated with the ICY track_processor plugin."""
    data = list(csv.reader(open(icy_file, "r")))
    name, extension = os.path.splitext(icy_file)

    with open(name + '_clean.csv', 'w', encoding='utf-8', newline='') as clean_file:
        writecsv = csv.writer(clean_file, quoting=csv.QUOTE_NONE)
        writecsv.writerow(['trackID', 'time', 'x', 'y', 'z'])
        for row in data:
            if len(row) > 0:
                # this is a non empty line
                if row[0].startswith('track'):
                    # this is a track line, trackID is second element
                    trackID = row[1]
                else:
                    if row[2] != 't' and row[2] != '':
                        temp_data = [float(trackID), float(row[2]), float(
                            row[3]), float(row[4]), float(row[5])]
                        writecsv.writerow(temp_data)
    clean_file.close()


def import_file(f, n):
    """Takes file from command line and # of rows to visualize.

    Keyword arguments:
    f -- the file (from command line)
    n -- number of rows to visualize (default 10)
    """

    if f.endswith('.xls'):
        try:
            xls_to_csv(f)
            name, extension = os.path.splitext(f)
            f = name + '.csv'
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
        print(f)
        for i in range(n):
            if i == 0:
                print('>>> header of the file:')
            elif i == 1:
                print('>>> rest of the file:')
            line = reader.readline()
            print(line)
            if line.startswith(',,,'):
                print(
                    'Trying to read an xls file generated with the ICY track_processor plugin.')
                print('The file will be cleaned up and reformatted.')
                clean_icy_file(f)
                name, extension = os.path.splitext(f)
                f = name + '_clean.csv'
                print('New file to work with: {}'.format(f))
                break
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
        print('Exiting now.')
        return


def split_in_objs_evnts(joint_id, grouped):
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
    events_df.columns = [joint_id, 'events_size']
    return {'objects': objects_df, 'events': events_df}
