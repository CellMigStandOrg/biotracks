# import needed libraries
import os
import datapackage as dp


def push_to_pandas(directory, joint_id):
    """Push the datapackage to a pandas storage.

    Keyword arguments:
    directory -- the directory to look into for the json descriptor
    joint_id -- the joint_identifier
    """
    descr = directory + os.sep + 'dp.json'
    storage = dp.push_datapackage(descriptor=descr, backend='pandas')
    print(storage.buckets)

    objects = stg['objects___objectstable']
    events = stg['events___eventstable']
    print(objects.head()), print(events.head())

    events.reset_index(inplace=True)
    print(events.head())

    # aggregation
    trajectories = pd.merge(objects, events, how='outer', on=joint_id)

    return trajectories
