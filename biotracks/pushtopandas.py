import os
import datapackage as dp
try:
    from datapackage.mappers import convert_path  # datapackage version 0.x
except ImportError:
    from datapackage.pushpull import _convert_path as convert_path
import pandas as pd

from .utils import NullLogger
from .names import OBJECTS_TABLE_NAME, LINKS_TABLE_NAME


def push_to_pandas(directory, object_id_cmso, logger=None):
    """Push a datapackage to a pandas storage.

    arguments:
    directory -- the datapackage directory containing the json file
    object_id_cmso -- the object id
    """
    if logger is None:
        logger = NullLogger()
    descr = directory + os.sep + 'dp.json'
    storage = dp.push_datapackage(descriptor=descr, backend='pandas')
    objects = storage[convert_path("objects.csv", OBJECTS_TABLE_NAME)]
    links = storage[convert_path("links.csv", LINKS_TABLE_NAME)]
    objects.reset_index(inplace=True)

    # aggregation to construct tracks
    tracks_dict = {}
    list_ = []
    TRACK_ID = -1
    for link in links.LINK_ID.unique():
        tmp = links[links.LINK_ID == link]
        rest = links[(links.LINK_ID != link) & (~links.LINK_ID.isin(list_))]
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
                    if link not in [l for v in tracks_dict.values() for l in v]:
                        TRACK_ID += 1
                        tracks_dict[TRACK_ID] = []
                    tracks_dict[TRACK_ID].append(link)
                    tracks_dict[TRACK_ID].append(rest.iloc[index].LINK_ID)
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
    tracks.columns = ['TRACK_ID', 'LINK_ID']
    return {'objects': objects, 'links': links, 'tracks': tracks}
