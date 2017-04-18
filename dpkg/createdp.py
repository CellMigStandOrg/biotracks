# import needed libraries
import collections
import csv
import io
import os
from collections import defaultdict

import datapackage as dp
import jsontableschema
from jsontableschema import infer


def create_dpkg(top_level_dict, dict_, directory, joint_id):
    """Create the datapackage representation.

    Keyword arguments:
    top_level_dict -- the dictionary with the TOP_LEVEL_INFO
    dict_ -- the dictionary containing objects and links
    directory -- the directory
    joint_id -- the joint_identifier
    """

    myDP = dp.DataPackage()

    for k, v in top_level_dict.items():
        myDP.descriptor[k] = v

    myDP.descriptor['resources'] = []

    # the objects block #
    key = 'objects'
    objects_table = dict_.get(key)
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

    # the links block #
    key = 'links'
    links_table = dict_.get(key)
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
