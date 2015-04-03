# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import configargparse
import sys

from twisted.python import log
from twisted.internet import reactor, task
from puntergatherer.common.settings import PGSettings


def def_args(parser):
    parser.add_argument('--debug',
                        help='Debug Info',
                        action='store_true',
                        default=False,
                        env_var='DEBUG',
                        )
    # GCM args
    parser.add_argument('--ttl',
                        env_var='GCM_TTL',
                        help='Time To Live',
                        type=int,
                        default=60,
                        )
    parser.add_argument('--dryrun',
                        env_var='GCM_DRYRUN',
                        help='Dry Run (no distribution)',
                        action='store_true',
                        default=False,
                        )
    parser.add_argument('--collapsekey',
                        env_var='GCM_COLLAPSEKEY',
                        help='string to collapse messages',
                        type=str,
                        default='simplepush',
                        )
    parser.add_argument('--apikey',
                        env_var='GCM_APIKEY',
                        help='API Key',
                        type=str,
                        )

def _settings(args, **kwargs):
    return PGSettings(args, **kwargs)

def main():
    sysargs = sys.argv[1:]
    log.startLogging(sys.stdout)

    parser = configargparse.ArgumentParse(
        description='GCM PunterGatherer',
        default_config_files=['/etc/.puntergatherer_gcm',
                              '~/.puntergatherer_gcm',
                              '.puntergatherer_gcm'])
    def_args(parser)
    settings = _settings(parser.parse_args(sysargs))
    loop = task.LoopingCall(




