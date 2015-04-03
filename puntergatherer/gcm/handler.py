# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import gcmclient

from twisted.internet import protocol
from twisted.python import log

from puntergatherer.common.exceptions import (
    MissingTokenErr,
    BadBridgeErr,
    InvalidTokenErr,
)


MinBackoff = 1000
MaxBackoff = 1024000


class GCMPost(object):
    gcm = None
    ttl = 60
    dryRun = False
    collpaseKey = "simplepush"
    backoff = 1000
    maxIter = 10

    def __init__(self, config):
        if config.get('apiKey') is None:
            log.err('Missing configuration option: "%s"', 'apiKey')
            raise BadBridgeErr

        self.ttl = config.get("ttl", self.ttl)
        self.dryRun = int(config.get("dryRun", self.dryRun))
        self.collapseKey = config.get("collapseKey", self.collapseKey)

        self.gcm = gcmclient.GCM(config.get("apikey"))
        self.storage = config.storage
        log.msg("Starting gcm bridge")

    def updateToken(self, uaid, connectInfo, new_token):
        if self.storage is not None:
            connectInfo["token"] = new_token
            return self.storage.register_connect(uaid, connectInfo)
        raise InvalidTokenErr

    def removeToken(self, uaid, token):
        if self.storage is not None:
            return self.storage.unregister_connect(uaid)
        raise InvalidTokenErr

    def _transmit(self, payload, iter=0):
        if iter > self.maxIter:
            log.msg("Failed repeated attempts to send message")
            return False
        try:
            reply = self.gcm.send(payload)
        except gcmclient.GCMAuthenticationError, e:
            # This means that the GCM Auth token we're using is
            # either invalid or has been revoked. This is exceptionally
            # bad.
            log.err("CRITICAL: GCM Token Authentication Error %s" % e)
            raise e
        if reply.needs_retry():
            self.backoffDelay(1000)
            self.backoff = max(self.backoff + (random.rand(0, 256) * 1000),
                               MaxBackoff)
            return self._transmit(payload, iter + 1)

    def send(self, uaid, version, data, connectInfo, payload=None, iter=0):
        if connectInfo.get("token") is None:
            log.msg("Connect info missing 'token'")
            raise MissingTokenErr

        payload = self.gcm.JSONMessage(
            registration_ids=[connectInfo.get("token")],
            collapse_key=self.collapseKey,
            time_to_live=self.ttl,
            dry_run=self.dryRun,
            data={"Msg": data,
                  "Version": version}
        )

        reply = self._transmit(payload)
        if reply is False:
            return False
        import pdb; pdb.set_trace()
        # these probably don't need to be loops, since there's only one
        # message sent.
        for old_id, new_id in reply.canonical.items():
            self.updateToken(uaid, connectInfo, new_id)
        for reg_id, err_code in reply.failed.items():
            return False, err_code
        for reg_id in reply.not_registered.items():
            return self.removeToken(uaid, reg_id)
        for reg_id, msg_id in reply.success.items():
            return True, None


class GCMProtocol(protocol.ProcessProtocol):

    def __init__(self, settings):
        self.settings = settings
        self.gcm = GCMPost(settings)

    def connectionMade(self):
        self.transport.write(self.settings)

    #TODO: Complete
