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

import datapackage
import datapackage.registry
import datapackage.exceptions

from . import names
from .utils import get_logger


REQUIRED_FIELDS = {
    names.OBJECTS_TABLE_NAME: {names.OBJECT_NAME, names.FRAME_NAME,
                               names.X_COORD_NAME, names.Y_COORD_NAME},
    names.LINKS_TABLE_NAME: {names.LINK_NAME, names.OBJECT_NAME},
    names.TRACKS_TABLE_NAME: {names.TRACK_NAME, names.LINK_NAME},
}

FOREIGN_KEYS = [
    {"fields": names.OBJECT_NAME,
     "reference": {"fields": names.OBJECT_NAME,
                   "resource": names.OBJECTS_TABLE_NAME}}
]


def is_tabular(dp):
    if not isinstance(dp, datapackage.DataPackage):
        return False
    reg = datapackage.registry.Registry()
    return dp.schema.to_dict() == reg.get('tabular')


class ValidationError(datapackage.exceptions.ValidationError):
    pass


class Validator(object):

    def __init__(self, log_level=None):
        self.logger = get_logger(self.__class__.__name__, level=log_level)

    def validate(self, dp):
        if isinstance(dp, datapackage.DataPackage) and not is_tabular(dp):
            raise ValueError("data package must be a tabular data package")
        else:
            dp = datapackage.DataPackage(dp, schema="tabular")
        dp.validate()
        self.logger.debug("valid tabular data package")
        if len(dp.resources) < 2:
            self.__error("data package must have at least two resources")
        res_map = dict((_.descriptor['name'], _) for _ in dp.resources)
        try:
            objects = res_map[names.OBJECTS_TABLE_NAME]
        except KeyError:
            self.__error("objects table not found")
        else:
            self.validate_objects(objects.descriptor)
        try:
            links = res_map[names.LINKS_TABLE_NAME]
        except KeyError:
            self.__error("links table not found")
        else:
            self.validate_links(links.descriptor)
        try:
            tracks = res_map[names.TRACKS_TABLE_NAME]
        except KeyError:
            pass
        else:
            self.validate_tracks(tracks.descriptor)

    def validate_objects(self, objects):
        try:
            pk = objects["schema"]["primaryKey"]
        except KeyError:
            self.__error("objects table schema has no primary key")
        if pk != names.OBJECT_NAME:
            self.__error(
                "objects table primary key must be %r" % (names.OBJECT_NAME,)
            )
        by_name = self.__check_required_fields(objects)
        id_field = by_name[names.OBJECT_NAME]
        try:
            constraints = id_field["constraints"]
        except KeyError:
            self.__error("object id field has no constraints")
        try:
            unique = constraints["unique"]
        except KeyError:
            self.__error("object id constraints: missing 'unique' property")
        if not unique:
            self.__error("object id constraints: 'unique' property is false")

    def validate_links(self, links):
        try:
            fk = links["schema"]["foreignKeys"]
        except KeyError:
            self.__error("objects table schema has no foreign keys")
        self.validate_foreign_keys(fk)
        self.__check_required_fields(links)

    def validate_tracks(self, tracks):
        self.__check_required_fields(tracks)

    def validate_foreign_keys(self, fk):
        if len(fk) != 1:
            self.__error("links table must have exactly one foreign key")
        fk = fk[0]
        try:
            fields = fk["fields"]
            ref = fk["reference"]
        except KeyError as e:
            self.__error("missing property in foreignKeys: %r" % e.args)
        if fields != names.OBJECT_NAME:
            self.__error(
                "foreignKeys fields must be %r" % (names.OBJECT_NAME,)
            )
        try:
            ref_fields = ref["fields"]
            ref_res = ref["resource"]
        except KeyError as e:
            self.__error(
                "missing property in foreignKeys reference: %r" % e.args
            )
        if ref_fields != names.OBJECT_NAME:
            self.__error(
                "foreignKeys ref fields must be %r" % (names.OBJECT_NAME,)
            )
        if ref_res != names.OBJECTS_TABLE_NAME:
            self.__error(
                "foreignKeys ref resource must be %r" % (
                    names.OBJECTS_TABLE_NAME,)
            )

    def __check_required_fields(self, descriptor):
        required = REQUIRED_FIELDS[descriptor['name']]
        by_name = dict((_['name'], _) for _ in descriptor['schema']['fields'])
        if not required <= set(by_name):
            self.__error(
                "required fields for %s: %r" % (descriptor['name'], required)
            )
        return by_name

    def __error(self, msg):
        self.logger.error(msg)
        raise ValidationError(msg)
