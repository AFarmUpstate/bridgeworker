# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import configargparse

from twisted.python import log


def def_args(parser):
    parser.add_argument('--debug',
                        help='Debug Info',
                        action='store_true',
                        default=False,
                        env_var='DEBUG',
                       )
    parser.add_argument('--debug',
                        help='Debug Info',
                        action='store_true',
                        default=False,
                        env_var='DEBUG',
                       )


def main():



main()

