# #%L
# Copyright (c) 2016-2017 Cell Migration Standardisation Organization
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%

import xml.etree.ElementTree as ET

import pandas as pd
import xlrd

from .utils import get_logger
from .names import (
    X_COORD_NAME, Y_COORD_NAME, FRAME_NAME, OBJECT_NAME, LINK_NAME
)


class TracksReader(object):

    def __init__(self, fname, conf=None, log_level=None):
        self.fname = fname
        self.conf = conf or {}
        reader_name = self.__class__.__name__
        self.logger = get_logger(reader_name, level=log_level)
        self.logger.info('%s Reading "%s"', reader_name, fname)


class TrackMateReader(TracksReader):

    def read(self):
        self.root = ET.parse(self.fname).getroot()
        self.logger.info('Reading a TrackMate XML file version %s',
                         self.root.attrib.get('version'))
        spots_dict = self.read_spots()
        objects_df = pd.DataFrame(
            [[k, v[0], v[1], v[2]] for k, v in spots_dict.items()],
            columns=["SPOT_ID", "FRAME", "POSITION_X", "POSITION_Y"]
        )
        ordered_edges_df = self.read_edges(spots_dict)
        links_df = self.read_links(ordered_edges_df)
        return objects_df, links_df

    def read_spots(self):
        spots_dict = {}
        for child in self.root.find('Model'):
            if child.tag == 'AllSpots':
                spots = child
                for spot_in_frame in spots.getchildren():
                    for spot in spot_in_frame.getchildren():
                        spot_id = int(spot.get('ID'))
                        frame = int(spot.get('FRAME'))
                        position_x = float(spot.get('POSITION_X'))
                        position_y = float(spot.get('POSITION_Y'))
                        spots_dict[spot_id] = [frame, position_x, position_y]
        self.logger.debug('Found %d unique spots', len(spots_dict))
        return spots_dict

    def read_edges(self, spots_dict):
        edges_dict = {}
        edge_id = 0
        for child in self.root.find('Model'):
            if child.tag == 'AllTracks':
                tracks = child
                for track in tracks.getchildren():
                    track_id = int(track.get('TRACK_ID'))
                    for edge in track.getchildren():
                        spot_source_id = int(edge.get('SPOT_SOURCE_ID'))
                        spot_target_id = int(edge.get('SPOT_TARGET_ID'))
                        source_frame = spots_dict.get(spot_source_id)[0]
                        target_frame = spots_dict.get(spot_target_id)[0]
                        edges_dict[edge_id] = [
                            track_id,
                            spot_source_id,
                            spot_target_id,
                            source_frame,
                            target_frame
                        ]
                        edge_id += 1
        self.logger.debug('Found %d unique edges', len(edges_dict))

        # dictionary into pandas dataframe
        edges_df = pd.DataFrame(
            [[key, value[0], value[1], value[2], value[3], value[4]]
             for key, value in edges_dict.items()],
            columns=['EDGE_ID', 'TRACK_ID', 'SPOT_SOURCE_ID', 'SPOT_TARGET_ID',
                     'SOURCE_FRAME', 'TARGET_FRAME']
        )
        ordered_edges_df = edges_df.sort_values(
            ['TRACK_ID', 'SOURCE_FRAME', 'TARGET_FRAME'])
        ordered_edges_df.reset_index(inplace=True)

        # compute the differences across successive rows in frame,
        # spot_source and spot_target
        ordered_edges_df['FRAME_DIFF'] = ordered_edges_df.groupby(
            'TRACK_ID')['SOURCE_FRAME'].diff()
        ordered_edges_df['SPOT_SOURCE_DIFF'] = ordered_edges_df.groupby(
            'TRACK_ID')['SPOT_SOURCE_ID'].diff()
        ordered_edges_df['SPOT_TARGET_DIFF'] = ordered_edges_df.groupby(
            'TRACK_ID')['SPOT_TARGET_ID'].diff()

        # create the 'EVENT' column
        ordered_edges_df['EVENT'] = ['None'] * len(ordered_edges_df)
        for i in range(len(ordered_edges_df)):
            tmp = ordered_edges_df.iloc[i]
            # if frame diff is 1: no events
            if tmp['FRAME_DIFF'] == 0:
                if tmp['SPOT_SOURCE_DIFF'] == 0:
                    ordered_edges_df.loc[i, 'EVENT'] = 'split'
                elif tmp['SPOT_TARGET_DIFF'] == 0:
                    ordered_edges_df.loc[i, 'EVENT'] = 'merge'
            elif tmp['FRAME_DIFF'] > 1:
                ordered_edges_df.loc[i, 'EVENT'] = 'gap'
        # shift the event one row up
        ordered_edges_df.EVENT = ordered_edges_df.EVENT.shift(-1)
        return ordered_edges_df

    def read_links(self, ordered_edges_df):
        links_dict = {}
        link_id = 0
        for track in ordered_edges_df.TRACK_ID.unique():
            event = False
            tmp = ordered_edges_df[
                ordered_edges_df.TRACK_ID == track
            ].reset_index()
            links_dict[link_id] = []
            for index, row in tmp.iterrows():
                if row['EVENT'] == 'None' and event is False:
                    links_dict[link_id].append(row['SPOT_SOURCE_ID'])
                    links_dict[link_id].append(row['SPOT_TARGET_ID'])
                    # if source at row zero is not the same as target at row 1,
                    # flag an event
                    if tmp.shape[0] > 1:  # if number rows > 1
                        if (index == 0 and tmp.iloc[index].SPOT_TARGET_ID !=
                            tmp.iloc[index + 1].SPOT_SOURCE_ID):
                            link_id += 1
                            links_dict[link_id] = []
                            event = True
                elif row['EVENT'] == 'split':
                    event = True
                    link_id += 1
                    links_dict[link_id] = []
                    links_dict[link_id].append(row['SPOT_SOURCE_ID'])
                    links_dict[link_id].append(row['SPOT_TARGET_ID'])
                elif row['EVENT'] == 'merge':
                    event = True
                    for key, val in links_dict.items():
                        if row['SPOT_SOURCE_ID'] == val[-1]:
                            links_dict[key].append(row['SPOT_TARGET_ID'])
                            links_dict[key].append(row['SPOT_SOURCE_ID'])
                elif row['EVENT'] == 'gap':
                    if event is False:
                        links_dict[link_id].append(row['SPOT_SOURCE_ID'])
                        links_dict[link_id].append(row['SPOT_TARGET_ID'])
                    elif event is True:
                        for key, val in links_dict.items():
                            if row['SPOT_SOURCE_ID'] == val[-1]:
                                links_dict[key].append(row['SPOT_TARGET_ID'])
                                links_dict[key].append(row['SPOT_SOURCE_ID'])
                    link_id += 1
                    links_dict[link_id] = []
                elif row['EVENT'] == 'None' and event is True:
                    for key, val in links_dict.items():
                        if not val:
                            links_dict[key].append(row['SPOT_SOURCE_ID'])
                            links_dict[key].append(row['SPOT_TARGET_ID'])
                        if row['SPOT_SOURCE_ID'] == val[-1]:
                            links_dict[key].append(row['SPOT_SOURCE_ID'])
                            links_dict[key].append(row['SPOT_TARGET_ID'])
            link_id += 1

        # get only unique spots
        links_dict_unique = {}
        for key, value in links_dict.items():
            unique_set = set(value)
            links_dict_unique[key] = unique_set
        self.logger.debug('Created %d links', len(links_dict_unique))
        links_df = pd.DataFrame()
        for key, value in links_dict_unique.items():
            for spot in value:
                links_df = links_df.append([[key, spot]], ignore_index=True)
        links_df.columns = ['LINK_ID', 'SPOT_ID']
        return links_df


class CellProfilerReader(TracksReader):

    def read(self):
        self.x = self.conf.get(X_COORD_NAME)
        self.y = self.conf.get(Y_COORD_NAME)
        self.frame = self.conf.get(FRAME_NAME)
        self.obj_id = self.conf.get(OBJECT_NAME)
        # parse the digits used for the tracking settings (e.g. 15)
        digits = self.x.split('_')[2]
        self.track_id = 'TrackObjects_Label_' + digits
        self.parent_obj_id = 'TrackObjects_ParentObjectNumber_' + digits
        self.parent_img_id = 'TrackObjects_ParentImageNumber_' + digits
        cp_df, objects_df = self.read_objects()
        links_df = self.read_links(cp_df)
        return objects_df, links_df

    def read_objects(self):
        objects_dict = {}
        cp_df = pd.read_csv(self.fname)
        cp_df = cp_df.sort_values([self.track_id, self.frame])
        # create new object identifiers
        cp_df.reset_index(inplace=True)
        for index, row in cp_df.iterrows():
            objects_dict[index] = [row[self.frame], row[self.x], row[self.y]]
            objects_df = pd.DataFrame(
                [[key, value[0], value[1], value[2]]
                 for key, value in objects_dict.items()],
                columns=[self.obj_id, self.frame, self.x, self.y]
            )
        return cp_df, objects_df

    def read_links(self, cp_df):
        links_dict = {}
        LINK_ID = 0
        unique_parent_object = 0
        for track in cp_df[self.track_id].unique():
            tmp = cp_df[cp_df[self.track_id] == track]
            for index, row in tmp.iterrows():
                if index == 0:
                    links_dict[LINK_ID] = [index]
                else:
                    parentImage = row[self.parent_img_id]
                    parentObject = row[self.parent_obj_id]
                    for j, r in tmp.iterrows():
                        if (r.ObjectNumber == parentObject and
                            r[self.frame] == parentImage):
                            unique_parent_object = j
                            break
                    if row.ObjectNumber == row[self.parent_obj_id]:
                        for key, val in links_dict.items():
                            if unique_parent_object == val[-1]:
                                links_dict[key].append(index)
                                break
                    else:
                        LINK_ID += 1
                        links_dict[LINK_ID] = []
                        if row[self.parent_obj_id] != 0:
                            links_dict[LINK_ID].append(unique_parent_object)
                        links_dict[LINK_ID].append(index)
        links_df = pd.DataFrame()
        for key, value in links_dict.items():
            for object_ in value:
                links_df = links_df.append([[key, object_]])
        links_df.columns = [self.conf.get(LINK_NAME), self.obj_id]
        return links_df


class IcyReader(TracksReader):

    def read(self):
        book = xlrd.open_workbook(self.fname)
        sheet = book.sheet_by_index(0)
        track = None
        obj = 0
        objects, links = [], []
        for i in range(sheet.nrows):
            values = sheet.row_values(i)
            if values[0]:  # track number line
                track = int(values[1])
            elif type(values[2]) is float:  # data line
                objects.append([obj] + values[2:6])
                links.append([track, obj])
                obj += 1
        obj_df = pd.DataFrame(
            objects, columns=['OBJECT_ID', 't', 'x', 'y', 'z']
        )
        links_df = pd.DataFrame(links, columns=['LINK_ID', 'OBJECT_ID'])
        return obj_df, links_df


def read_file(fname, track_dict, log_level=None):
    if fname.endswith('.xls'):
        objects, links = IcyReader(fname, log_level=log_level).read()
    elif fname.endswith('.xml'):
        objects, links = TrackMateReader(fname, log_level=log_level).read()
    elif fname.endswith('.csv'):
        objects, links = CellProfilerReader(
            fname, conf=track_dict, log_level=log_level
        ).read()
    return {'objects': objects, 'links': links}
