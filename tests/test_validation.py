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

import json
import csv
from copy import deepcopy

import pytest
from datapackage.exceptions import ValidationError

from biotracks import validation, names

OBJECTS_PATH = "objects.csv"
LINKS_PATH = "links.csv"
TRACKS_PATH = "tracks.csv"
JSON = {
    "name": names.PACKAGE_NAME,
    "resources": [
        {
            "name": names.OBJECTS_TABLE_NAME,
            "path": OBJECTS_PATH,
            "schema": {
                "fields": [
                    {"name": names.OBJECT_NAME,
                     "constraints": {"unique": True}},
                    {"name": names.FRAME_NAME},
                    {"name": names.X_COORD_NAME},
                    {"name": names.Y_COORD_NAME},
                ],
                "primaryKey": names.OBJECT_NAME,
            }
        },
        {
            "name": names.LINKS_TABLE_NAME,
            "path": LINKS_PATH,
            "schema": {
                "fields": [{"name": names.LINK_NAME},
                           {"name": names.OBJECT_NAME}],
                "foreignKeys": [
                    {"fields": names.OBJECT_NAME,
                     "reference": {"fields": names.OBJECT_NAME,
                                   "resource": names.OBJECTS_TABLE_NAME}}
                ]
            }
        }
    ]
}

CSV = {
    OBJECTS_PATH: [
        [names.OBJECT_NAME, names.FRAME_NAME,
         names.X_COORD_NAME, names.Y_COORD_NAME],
        [0, 1, 0.4, 0.5],
        [1, 2, 0.5, 0.6],
    ],
    LINKS_PATH: [
        [names.LINK_NAME, names.OBJECT_NAME],
        [0, 0],
        [0, 1],
    ],
}


@pytest.fixture()
def dp(tmpdir):
    def make_dp(descriptor):
        json_path = tmpdir.join("dp.json")
        with json_path.open("w") as f:
            json.dump(descriptor, f)
        for name, content in CSV.items():
            with tmpdir.join(name).open("w") as f:
                csv.writer(f).writerows(content)
        return str(json_path)
    yield make_dp
    tmpdir.remove(rec=True)


class TestValidation(object):

    def test_validation(self, dp):
        validation.Validator().validate(dp(JSON))

    def test_no_name(self, dp):
        d = deepcopy(JSON)
        del d["name"]
        self.__assert_raises(dp(d))

    def test_no_resources(self, dp):
        d = deepcopy(JSON)
        del d["resources"]
        self.__assert_raises(dp(d))

    def test_bad_name(self, dp):
        d = deepcopy(JSON)
        d["name"] = d["name"].upper()
        self.__assert_raises(dp(d))

    def test_missing_resource(self, dp):
        for i in range(len(JSON["resources"])):
            d = deepcopy(JSON)
            del d["resources"][i]
            self.__assert_raises(dp(d))

    def test_missing_field(self, dp):
        for i, res in enumerate(JSON["resources"]):
            for j in range(len(res["schema"]["fields"])):
                d = deepcopy(JSON)
                del d["resources"][i]["schema"]["fields"][j]
                self.__assert_raises(dp(d))

    def test_primary_key(self, dp):
        obj_i, obj_res = self.__res_by_name(names.OBJECTS_TABLE_NAME)
        d = deepcopy(JSON)
        del d["resources"][obj_i]["schema"]["primaryKey"]
        self.__assert_raises(dp(d))
        d = deepcopy(JSON)
        d["resources"][obj_i]["schema"]["primaryKey"] = "foobar"
        self.__assert_raises(dp(d))

    def test_constraints(self, dp):
        i, r = self.__res_by_name(names.OBJECTS_TABLE_NAME)
        j = [_ for (_, f) in enumerate(r["schema"]["fields"])
             if f["name"] == names.OBJECT_NAME][0]
        d = deepcopy(JSON)
        del d["resources"][i]["schema"]["fields"][j]["constraints"]
        self.__assert_raises(dp(d))
        d = deepcopy(JSON)
        d["resources"][i]["schema"]["fields"][j]["constraints"] = {}
        self.__assert_raises(dp(d))
        d = deepcopy(JSON)
        d["resources"][i]["schema"]["fields"][j]["constraints"]["unique"] = 0
        self.__assert_raises(dp(d))

    def test_foreign_keys(self, dp):
        i, r = self.__res_by_name(names.LINKS_TABLE_NAME)
        d = deepcopy(JSON)
        del d["resources"][i]["schema"]["foreignKeys"]
        self.__assert_raises(dp(d))
        d = deepcopy(JSON)
        d["resources"][i]["schema"]["foreignKeys"][0]["fields"] = ""
        self.__assert_raises(dp(d))
        for k in "fields", "resource":
            d = deepcopy(JSON)
            d["resources"][i]["schema"]["foreignKeys"][0]["reference"][k] = ""
            self.__assert_raises(dp(d))

    def test_tracks(self, dp):
        tracks_res = {
            "name": names.TRACKS_TABLE_NAME,
            "path": TRACKS_PATH,
            "schema": {
                "fields": [
                    {"name": names.TRACK_NAME},
                    {"name": names.LINK_NAME},
                ],
            },
        }
        d = deepcopy(JSON)
        d["resources"].append(tracks_res)
        validation.Validator().validate(dp(d))
        for i in range(len(tracks_res["schema"]["fields"])):
            d = deepcopy(JSON)
            r = deepcopy(tracks_res)
            del r["schema"]["fields"][i]
            d["resources"].append(r)
            self.__assert_raises(dp(d))

    def __res_by_name(self, name):
        return [(i, r) for (i, r) in enumerate(JSON["resources"])
                if r["name"] == name][0]

    def __assert_raises(self, dp_fn):
        with pytest.raises(ValidationError):
            validation.Validator().validate(dp_fn)
