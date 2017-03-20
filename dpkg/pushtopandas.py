# import needed libraries
import os
import datapackage as dp
import pandas as pd

def push_to_pandas(directory):
    """Push the datapackage to a pandas storage.

    Keyword arguments:
    directory -- the directory to look into for the json descriptor
    """
    descr = directory + os.sep + 'dp.json'
    storage = dp.push_datapackage(descriptor=descr, backend='pandas')
    print(storage.buckets)

    objects = storage['objects___objectstable']
    links = storage['links___linkstable']

    objects.reset_index(inplace=True)
    print(objects.head()), print(links.head())

    # simple aggregation
    # trajectories --> this will be a dataframe with link_id, track_id
    # look at pair wise comparison across link_ids in the links dataframe

    return {'objects' : objects, 'links' : links, 'trajectories' : trajectories}
