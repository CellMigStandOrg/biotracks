import csv
import io
import os

import datapackage as dp
from jsontableschema import infer
from .names import OBJECTS_TABLE_NAME, LINKS_TABLE_NAME


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
    path = key + '.csv'
    with io.open(directory + os.sep + key + '.csv') as stream:
        headers = stream.readline().rstrip('\n').split(',')
        values = csv.reader(stream)
        schema = infer(headers, values, row_limit=50,
                       primary_key=joint_id)

    myDP.descriptor['resources'].append(
        {"name": OBJECTS_TABLE_NAME,
         "path": path,
         "schema": schema,
         }
    )

    # the links block #
    key = 'links'
    path = key + '.csv'
    with io.open(directory + os.sep + key + '.csv') as stream:
        headers = stream.readline().rstrip('\n').split(',')
        values = csv.reader(stream)
        schema = infer(headers, values, row_limit=50)
        schema['foreignKeys'] = [{
            "fields": joint_id,
            "reference": {
                "datapackage": "",
                "resource": OBJECTS_TABLE_NAME,
                "fields": joint_id
            }
        }]

    myDP.descriptor['resources'].append(
        {"name": LINKS_TABLE_NAME,
         "path": path,
         "schema": schema,
         }
    )

    return myDP
