# import needed libraries
import io
import os
import csv
import datapackage as dp
import jsontableschema
from jsontableschema import infer
import collections
from collections import defaultdict


def top_level_info():
    """Returns a dictionary for the top level information."""
    author = 'author'
    author_email = 'author@email.com'

    top = (
        ('title', 'cell tracking file'),
        ('name', 'tracking-file'),
        ('author', author),
        ('author_email', author_email)
    )

    top_dict = defaultdict(list)
    for k, v in top:
        top_dict[k].append((v))

    print('The top_dict: {}'.format(top_dict.items()))
    return top_dict


def create_dpkg(dictionary, directory, joint_id):
    """Create the datapackage representation.

    Keyword arguments:
    dictionary -- the dictionary containing events and objects
    directory -- the directory
    joint_id -- the joint_identifier
    """

    top_dict = top_level_info()
    myDP = dp.DataPackage()

    for k, v in top_dict.items():
        myDP.descriptor[k] = v

    myDP.descriptor['resources'] = []

    # the events block #
    key = 'events'
    events_table = dictionary.get(key)
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
    objects_table = dictionary.get(key)
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
