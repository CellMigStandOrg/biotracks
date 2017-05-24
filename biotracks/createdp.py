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
