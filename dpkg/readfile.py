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


def read_trackMate(trackMate_file):
    """Utility function to read a TrackMate XML file and convert it to a plain csv."""

    tree = ET.parse(trackMate_file)
    root = tree.getroot()
    print('>>>')
    print('Reading a TrackMate XML file version {}'.format(
        root.attrib.get('version')))

    ################################
    ### dictionary for the spots ###
    ################################
    spots_dict = {}
    for child in root.find('Model'):
        if child.tag == 'AllSpots':
            spots = child
            for spot_in_frame in spots.getchildren():
                for spot in spot_in_frame.getchildren():
                    # the key
                    SPOT_ID = int(spot.get('ID'))
                    # the value
                    FRAME = int(spot.get('FRAME'))
                    POSITION_X = float(spot.get('POSITION_X'))
                    POSITION_Y = float(spot.get('POSITION_Y'))
                    # insert into dict {frame, x, y}
                    spots_dict[SPOT_ID] = [FRAME, POSITION_X, POSITION_Y]
            break
    print('>>> Found {} unique spots'.format(len(spots_dict)))

    # dictionary into pandas dataframe
    name, extension = os.path.splitext(trackMate_file)
    objects_df = pd.DataFrame([[key, value[0], value[1], value[2]] for key, value in spots_dict.items()], columns=[
        "SPOT_ID", "FRAME", "POSITION_X", "POSITION_Y"])
    # write the objects dataframe to a csv file
    #objects_df.to_csv(name + '_CMSO_objects.csv', index=False)

    ################################
    ### dictionary for the edges ###
    ################################
    edges_dict = {}
    EDGE_ID = 0  # the key
    for child in root.find('Model'):
        if child.tag == 'AllTracks':
            tracks = child
            for track in tracks.getchildren():
                TRACK_ID = int(track.get('TRACK_ID'))
                for edge in track.getchildren():
                    SPOT_SOURCE_ID = int(edge.get('SPOT_SOURCE_ID'))
                    SPOT_TARGET_ID = int(edge.get('SPOT_TARGET_ID'))
                    SOURCE_FRAME = spots_dict.get(SPOT_SOURCE_ID)[0]
                    TARGET_FRAME = spots_dict.get(SPOT_TARGET_ID)[0]
                    # insert {key, value}
                    edges_dict[EDGE_ID] = [TRACK_ID, SPOT_SOURCE_ID,
                                           SPOT_TARGET_ID, SOURCE_FRAME, TARGET_FRAME]
                    EDGE_ID += 1
            break

    print('>>> Found {} unique edges'.format(len(edges_dict)))

    # dictionary into pandas dataframe
    edges_df = pd.DataFrame([[key, value[0], value[1], value[2], value[3], value[4]] for key, value in edges_dict.items()], columns=[
        "EDGE_ID", "TRACK_ID", "SPOT_SOURCE_ID", "SPOT_TARGET_ID", "SOURCE_FRAME", "TARGET_FRAME"])
    # order the df
    ordered_edges_df = edges_df.sort_values(
        ['TRACK_ID', 'SOURCE_FRAME', 'TARGET_FRAME'])
    ordered_edges_df.reset_index(inplace=True)
    # compute the differences across successive rows in frame, spot_source and
    # spot_target
    ordered_edges_df['FRAME_DIFF'] = ordered_edges_df.groupby('TRACK_ID')[
        'SOURCE_FRAME'].diff()
    ordered_edges_df['SPOT_SOURCE_DIFF'] = ordered_edges_df.groupby('TRACK_ID')[
        'SPOT_SOURCE_ID'].diff()
    ordered_edges_df['SPOT_TARGET_DIFF'] = ordered_edges_df.groupby('TRACK_ID')[
        'SPOT_TARGET_ID'].diff()

    # create the 'EVENT' column to be added to the df
    ordered_edges_df['EVENT'] = ['None'] * len(ordered_edges_df)

    for i in range(len(ordered_edges_df)):
        tmp = ordered_edges_df.iloc[i]
        # if difference in frame is 1: no events
        if tmp['FRAME_DIFF'] == 0:
            # if difference of spot source is zero - split event
            if tmp['SPOT_SOURCE_DIFF'] == 0:
                ordered_edges_df.loc[i, 'EVENT'] = 'split'
            elif tmp['SPOT_TARGET_DIFF'] == 0:
                # if difference of spot target is zero - merge event
                ordered_edges_df.loc[i, 'EVENT'] = 'merge'
        # if difference of frame is bigger than 1 - gap event
        elif tmp['FRAME_DIFF'] > 1:
            ordered_edges_df.loc[i, 'EVENT'] = 'gap'
    # shift the event one row up
    ordered_edges_df.EVENT = ordered_edges_df.EVENT.shift(-1)

    ################################
    ### dictionary for the links ###
    ################################
    links_dict = {}
    # initialize id for the link
    LINK_ID = 0

    for track in ordered_edges_df.TRACK_ID.unique():
        event = False
        tmp = ordered_edges_df[
            ordered_edges_df.TRACK_ID == track].reset_index()
        links_dict[LINK_ID] = []
        for index, row in tmp.iterrows():

            if row['EVENT'] == 'None' and event is False:
                links_dict[LINK_ID].append(row['SPOT_SOURCE_ID'])
                links_dict[LINK_ID].append(row['SPOT_TARGET_ID'])
                # if source at row zero is not the same as target at row 1,
                # flag an event
                if tmp.shape[0] > 1: # if number rows > 1
                    if index == 0 and (tmp.iloc[index].SPOT_TARGET_ID) != (tmp.iloc[index + 1].SPOT_SOURCE_ID):

                        LINK_ID += 1
                        links_dict[LINK_ID] = []
                        event = True

            elif row['EVENT'] == 'split':
                event = True
                LINK_ID += 1
                links_dict[LINK_ID] = []
                links_dict[LINK_ID].append(row['SPOT_SOURCE_ID'])
                links_dict[LINK_ID].append(row['SPOT_TARGET_ID'])

            elif row['EVENT'] == 'merge':
                event = True
                for key, val in links_dict.items():
                    if row['SPOT_SOURCE_ID'] == val[-1]:
                        links_dict[key].append(row['SPOT_TARGET_ID'])
                        links_dict[key].append(row['SPOT_SOURCE_ID'])

            elif row['EVENT'] == 'gap':
                if event is False:
                    links_dict[LINK_ID].append(row['SPOT_SOURCE_ID'])
                    links_dict[LINK_ID].append(row['SPOT_TARGET_ID'])

                elif event is True:
                    for key, val in links_dict.items():
                        if row['SPOT_SOURCE_ID'] == val[-1]:
                            links_dict[key].append(row['SPOT_TARGET_ID'])
                            links_dict[key].append(row['SPOT_SOURCE_ID'])
                LINK_ID += 1
                links_dict[LINK_ID] = []

            elif row['EVENT'] == 'None' and event is True:
                for key, val in links_dict.items():
                    if not val:
                        links_dict[key].append(row['SPOT_SOURCE_ID'])
                        links_dict[key].append(row['SPOT_TARGET_ID'])
                    if row['SPOT_SOURCE_ID'] == val[-1]:
                        links_dict[key].append(row['SPOT_SOURCE_ID'])
                        links_dict[key].append(row['SPOT_TARGET_ID'])

        LINK_ID += 1

    # get only the unique spots
    links_dict_unique = {}
    for key, value in links_dict.items():
        unique_set = set(value)
        links_dict_unique[key] = unique_set
    print('>>> Created {} links'.format(len(links_dict_unique)))

    links_df = pd.DataFrame()
    for key, value in links_dict_unique.items():
        for spot in value:
            links_df = links_df.append([[key, spot]], ignore_index=True)
    links_df.columns = ['LINK_ID', 'SPOT_ID']
    #links_df.to_csv(name + '_CMSO_links.csv', index=False)

    return (objects_df, links_df)


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


def read_file(f):
    """Takes file from command line.

    Keyword arguments:
    f -- the file (from command line)
    """
    # check for file extension
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
        (objects, links) = read_trackMate(f)
        print('Successfully parsed a TrackMate XML file...')

    # show objects and links previews
    print('>>> showing objects dataframe...')
    print(objects.head())
    print('>>> showing links dataframe...')
    print(links.head())

    return {'objects' : objects, 'links' : links}


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
