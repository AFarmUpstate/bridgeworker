# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import configargparse
import sys
from bridgeworker.common.settings import Settings
from bridgeworker.gcm.gcm import GCM

from twisted.python import log
from twisted.internet import reactor
from twisted.spread import pb

config_files = [
    '/etc/gcm_bridge.ini',
    '~/.gcm_bridge.ini',
    '.gcm_bridge.ini',
]


def def_args(sysargs=None):
    if sysargs is None:
        sysargs = sys.argv[1:]

    parser = configargparse.ArgumentParser(
        description="Manages third party bridge connections",
        default_config_files=config_files)
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
    args = parser.parse_args(sysargs)
    return args, parser


def main(sysargs=None):
    args, parser = def_args(sysargs)
    settings = Settings(args)

    gcm_serv = pb.PBServerFactory(GCM(settings))

    reactor.listenTCP(settings.get("port"), gcm_serv)
    reactor.run()


if __name__ == "__main__":
    main(sys.argv[1:])

