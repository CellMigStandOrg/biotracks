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
import os
import re

import datapackage
from jsontableschema import infer
from . import cmso, config
from .utils import get_logger, mkdir_p


# https://specs.frictionlessdata.io/data-package/#metadata
NAME_PATTERN = re.compile(r"^[a-z0-9_.-]+$")
FOREIGN_KEYS = [{
    "fields": cmso.OBJECT_ID,
    "reference": {
        "datapackage": "",
        "resource": cmso.OBJECTS_TABLE,
        "fields": cmso.OBJECT_ID
    }
}]


def infer_from_df(df, **kwargs):
    # df.iterrows does not preserve types
    h = df.head()
    fields = list(df)
    iterrows = ([str(h[_].values[i]) for _ in fields]
                for i in range(h.shape[0]))
    return infer(fields, iterrows, **kwargs)


def to_json(dp):
    return json.dumps(dp.to_dict(), indent=4, sort_keys=True)


def create(reader, out_dir, log_level=None):
    logger = get_logger("createdp.create", level=log_level)
    top_level_dict = reader.conf[config.TOP_LEVEL]
    try:
        name = top_level_dict["name"]
    except KeyError:
        raise ValueError("'name' is a required property")
    if not NAME_PATTERN.match(name):
        raise ValueError("invalid name: %r" % (name,))
    dp = datapackage.DataPackage()
    for k, v in top_level_dict.items():
        dp.descriptor[k] = v
    dp.descriptor['resources'] = []
    mkdir_p(out_dir)
    logger.info("writing to '%s'", out_dir)
    for a in "objects", "links":
        out_bn = "%s.csv" % a
        out_fn = os.path.join(out_dir, out_bn)
        df = getattr(reader, a)
        df.to_csv(out_fn, index=False, quoting=csv.QUOTE_NONE)
        if a == "objects":
            name = cmso.OBJECTS_TABLE
            infer_kwargs = {"primary_key": cmso.OBJECT_ID}
        else:
            name = cmso.LINKS_TABLE
            infer_kwargs = {}
        schema = infer_from_df(df, **infer_kwargs)
        if a == "links":
            schema['foreignKeys'] = FOREIGN_KEYS
        res = {"name": name, "path": out_bn, "schema": schema}
        dp.descriptor['resources'].append(res)
    with open(os.path.join(out_dir, 'dp.json'), 'w') as f:
        f.write(to_json(dp) + '\n')
    return dp
