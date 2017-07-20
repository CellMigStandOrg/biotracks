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

"""\
Reader objects for tracking data formats.
"""

import os
import xml.etree.ElementTree as ET
from abc import ABCMeta, abstractmethod

import pandas as pd
import xlrd

from .utils import get_logger
from .validation import Validator
from . import cmso, config


class AbstractReader(metaclass=ABCMeta):
    """\
    Common interface for all tracking data readers.
    """
    def __init__(self, fname, conf=None, log_level=None):
        """\
        Set the input file name for the reader.

        The ``conf`` argument is optional in the general case, but it
        may be required for a specific reader.

        Actual reading is supposed to happen when the ``read`` method
        is called.
        """
        reader_name = self.__class__.__name__
        self.logger = get_logger(reader_name, level=log_level)
        self.fname = fname
        self.conf = conf or config.get_conf()
        self.log_level = log_level
        self.logger.info('%s Reading "%s"', reader_name, fname)
        self._objects = None
        self._links = None

    @abstractmethod
    def read(self):
        """\
        Read the input file. The concrete implementation of this
        method should populate the _objects and _links attributes with
        dataframes containing the corresponding tracking data.  If the
        specific format contains additional information, for instance
        on time and space units, this should be added to the ``conf``
        object (if not already present).
        """
        return

    @property
    def objects(self):
        """\
        Return the objects dataframe, calling ``read`` if necessary.
        """
        if self._objects is None:
            self.read()
        return self._objects

    @property
    def links(self):
        """\
        Return the links dataframe, calling ``read`` if necessary.
        """
        if self._links is None:
            self.read()
        return self._links


class BiotracksReader(AbstractReader):

    def read(self):
        dp = Validator(log_level=self.log_level).validate(self.fname)
        d = os.path.dirname(self.fname)
        path_map = dict((_.descriptor["name"], _.descriptor["path"])
                        for _ in dp.resources)
        self._objects = pd.read_csv(
            os.path.join(d, path_map[cmso.OBJECTS_TABLE])
        )
        self._links = pd.read_csv(
            os.path.join(d, path_map[cmso.LINKS_TABLE])
        )
        for k in cmso.SPACE_UNIT, cmso.TIME_UNIT:
            try:
                v = dp.descriptor[k]
            except KeyError:
                pass
            else:
                self.conf[config.TOP_LEVEL].setdefault(k, v)


class TrackMateReader(AbstractReader):

    def read(self):
        self.root = ET.parse(self.fname).getroot()
        self.logger.info('Reading a TrackMate XML file version %s',
                         self.root.attrib.get('version'))
        self.__model = self.root.find('Model')
        self.conf[config.TOP_LEVEL].setdefault(
            cmso.SPACE_UNIT, self.__model.attrib["spatialunits"]
        )
        self.conf[config.TOP_LEVEL].setdefault(
            cmso.TIME_UNIT, self.__model.attrib["timeunits"]
        )
        spots_dict = self.read_spots()
        self._objects = pd.DataFrame(
            [[k, v[0], v[1], v[2]] for k, v in spots_dict.items()],
            columns=[cmso.OBJECT_ID, cmso.FRAME_ID, cmso.X_COORD, cmso.Y_COORD]
        )
        ordered_edges_df = self.read_edges(spots_dict)
        self._links = self.read_links(ordered_edges_df)

    def read_spots(self):
        spots_dict = {}
        for child in self.__model:
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
        for child in self.__model:
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
        links_df.columns = [cmso.LINK_ID, cmso.OBJECT_ID]
        return links_df


class CellProfilerReader(AbstractReader):

    def read(self):
        self.x = self.conf[config.TRACKING].get(cmso.X_COORD)
        self.y = self.conf[config.TRACKING].get(cmso.Y_COORD)
        self.frame = self.conf[config.TRACKING].get(cmso.FRAME_ID)
        self.obj_id = self.conf[config.TRACKING].get(cmso.OBJECT_ID)
        # parse the digits used for the tracking settings (e.g. 15)
        digits = self.x.split('_')[2]
        self.track_id = 'TrackObjects_Label_' + digits
        self.parent_obj_id = 'TrackObjects_ParentObjectNumber_' + digits
        self.parent_img_id = 'TrackObjects_ParentImageNumber_' + digits
        cp_df, self._objects = self.read_objects()
        self._links = self.read_links(cp_df)

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
        objects_df.columns = [
            cmso.OBJECT_ID, cmso.FRAME_ID, cmso.X_COORD, cmso.Y_COORD
        ]
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
        links_df.columns = [cmso.LINK_ID, cmso.OBJECT_ID]
        return links_df


class IcyReader(AbstractReader):

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
        self._objects = pd.DataFrame(
            objects, columns=['OBJECT_ID', 't', 'x', 'y', 'z']
        )
        self._objects.columns = [cmso.OBJECT_ID, cmso.FRAME_ID, cmso.X_COORD,
                                 cmso.Y_COORD, cmso.Z_COORD]
        self._links = pd.DataFrame(links, columns=['LINK_ID', 'OBJECT_ID'])
        self._links.columns = [cmso.LINK_ID, cmso.OBJECT_ID]


class CellmiaReader(AbstractReader):

    ENCODING = "iso-8859-1"
    SEP = "\t"

    def read(self):
        cellmia_link_id = "ID of track"
        x = self.conf[config.TRACKING].get(cmso.X_COORD)
        y = self.conf[config.TRACKING].get(cmso.Y_COORD)
        frame_id = self.conf[config.TRACKING].get(cmso.FRAME_ID)
        df = pd.read_csv(self.fname, sep=self.SEP, encoding=self.ENCODING,
                         usecols=[cellmia_link_id, frame_id, x, y])
        df.reset_index(inplace=True)
        df.columns = [cmso.OBJECT_ID, cmso.LINK_ID, cmso.FRAME_ID,
                      cmso.X_COORD, cmso.Y_COORD]
        self._objects = df.drop(cmso.LINK_ID, 1)
        self._links = df.drop([cmso.FRAME_ID, cmso.X_COORD, cmso.Y_COORD], 1)


class TracksReader(object):
    """\
    Generic reader that delegates to specific ones based on file extension.
    """
    def __init__(self, fname, conf=None, log_level=None):
        """\
        Initialize and store a specific reader based on filename extension.

        All other methods delegate to the specific reader.
        """
        logger = get_logger(self.__class__.__name__, level=log_level)
        _, ext = os.path.splitext(fname)
        if ext == '.xls':
            self.reader = IcyReader(fname, conf=conf, log_level=log_level)
        elif ext == '.xml':
            self.reader = TrackMateReader(
                fname, conf=conf, log_level=log_level
            )
        elif ext == '.csv':
            self.reader = CellProfilerReader(
                fname, conf=conf, log_level=log_level
            )
        elif ext == '.txt':
            self.reader = CellmiaReader(
                fname, conf=conf, log_level=log_level
            )
        elif ext == '.json':
            self.reader = BiotracksReader(
                fname, conf=conf, log_level=log_level
            )
        else:
            msg = '%r: unknown format: %r' % (fname, ext)
            logger.error(msg)
            raise RuntimeError(msg)

    def read(self):
        self.reader.read()

    @property
    def conf(self):
        return self.reader.conf

    @property
    def objects(self):
        return self.reader.objects

    @property
    def links(self):
        return self.reader.links
