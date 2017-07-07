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

"""\
Validate a CMSO datapackage.
"""

import sys
import argparse

from biotracks.validation import Validator
from biotracks.utils import get_log_level


def log_level(s):
    try:
        return get_log_level(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(e.message)


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dp_fn', metavar="JSON_FILE")
    parser.add_argument('--log-level', metavar='LEVEL', type=log_level,
                        default='INFO', help='logging level')
    return parser


def main(argv):
    parser = make_parser()
    args = parser.parse_args(argv[1:])
    validator = Validator(log_level=args.log_level)
    validator.validate(args.dp_fn)


if __name__ == "__main__":
    main(sys.argv)
