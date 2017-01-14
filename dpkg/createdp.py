# import needed libraries
import io
import os
import csv
import datapackage as dp
import jsontableschema
from jsontableschema import infer
import collections
from collections import defaultdict


def create_dpkg(top_level_dict, ev_ob_dict, directory, joint_id):
    """Create the datapackage representation.

    Keyword arguments:
    top_level_dict -- the dictionary with the TOP_LEVEL_INFO
    ev_ob_dict -- the dictionary containing events and objects
    directory -- the directory
    joint_id -- the joint_identifier
    """

    myDP = dp.DataPackage()

    for k, v in top_level_dict.items():
        myDP.descriptor[k] = v

    myDP.descriptor['resources'] = []

    # the events block #
    key = 'events'
    events_table = ev_ob_dict.get(key)
    path = key + '.csv'
    with io.open(directory + os.sep + key + '.csv') as stream:
        headers = stream.readline().rstrip('\n').split(',')
        values = csv.reader(stream)
        schema = infer(headers, values, row_limit=50,
                       primary_key=joint_id)
        referenced_resource = key + 'Table'

    myDP.descriptor['resources'].append(
        {"name": key + 'Table',
         "path": path,
         "schema": schema,
         }
    )

    # the objects block #
    key = 'objects'
    objects_table = ev_ob_dict.get(key)
    path = key + '.csv'
    with io.open(directory + os.sep + key + '.csv') as stream:
        headers = stream.readline().rstrip('\n').split(',')
        values = csv.reader(stream)
        schema = infer(headers, values, row_limit=50)
        schema['foreignKeys'] = [{
            "fields": joint_id,
            "reference": {
                "datapackage": "",
                "resource": referenced_resource,
                "fields": joint_id
            }
        }]

    myDP.descriptor['resources'].append(
        {"name": key + 'Table',
         "path": path,
         "schema": schema,
         }
    )

    return myDP
