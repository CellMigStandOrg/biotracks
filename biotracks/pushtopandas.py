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

import os
import datapackage as dp
try:
    from datapackage.mappers import convert_path  # datapackage version 0.x
except ImportError:
    from datapackage.pushpull import _convert_path as convert_path
import pandas as pd

from .utils import get_logger
from . import cmso


def push_to_pandas(directory, object_id_cmso, log_level=None):
    """Push a datapackage to a pandas storage.

    arguments:
    directory -- the datapackage directory containing the json file
    object_id_cmso -- the object id
    """
    logger = get_logger('push_to_pandas', level=log_level)
    descr = directory + os.sep + 'dp.json'
    storage = dp.push_datapackage(descriptor=descr, backend='pandas')
    objects = storage[convert_path("objects.csv", cmso.OBJECTS_TABLE)]
    links = storage[convert_path("links.csv", cmso.LINKS_TABLE)]
    objects.reset_index(inplace=True)

    # aggregation to construct tracks
    tracks_dict = {}
    list_ = []
    TRACK_ID = -1
    for link in links[cmso.LINK_ID].unique():
        tmp = links[links[cmso.LINK_ID] == link]
        rest = links[
            (links[cmso.LINK_ID] != link) & (~links[cmso.LINK_ID].isin(list_))
        ]
        ind = rest[object_id_cmso].isin(tmp[object_id_cmso])
        # no shared spots
        if not any(ind):
            # link not in dictionary
            if link not in [l for v in tracks_dict.values() for l in v]:
                TRACK_ID += 1
                tracks_dict[TRACK_ID] = [link]
        # shared spots
        if any(ind):
            for index, b in enumerate(ind):
                if b:
                    # link not in dictionary
                    if link not in [l for v in tracks_dict.values()
                                    for l in v]:
                        TRACK_ID += 1
                        tracks_dict[TRACK_ID] = []
                    tracks_dict[TRACK_ID].append(link)
                    tracks_dict[TRACK_ID].append(
                        rest.iloc[index][cmso.LINK_ID]
                    )
        list_.append(link)

    # get unique links and construct tracks dataframe
    tracks_dict_unique = {}
    for key, value in tracks_dict.items():
        unique_set = set(value)
        tracks_dict_unique[key] = unique_set
    logger.debug('Created %d tracks', len(tracks_dict_unique))
    tracks = pd.DataFrame()
    for key, value in tracks_dict_unique.items():
        for link in value:
            tracks = tracks.append([[key, link]], ignore_index=True)
    tracks.columns = [cmso.TRACK_ID, cmso.LINK_ID]
    return {'objects': objects, 'links': links, 'tracks': tracks}
