# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import apns

from twisted.python import log
from puntergatherer.common.exceptions import (
    MissingTokenErr,
    BadBridgeErr,
    InvalidTokenErr,


class APNSPost(object):
    apns = None
    defaultTitle = "SimplePush"
    defaultBody = "New Alert"

    def __init__(self, config):
        ok = True
        conferr = 'Missing configuration option: "%s"'
        for req in ['cert_file', 'key_file']:
            if config.get(req) is None:
                log.err(conferr % req)
                ok = False
        if not ok:
            raise BadBridgeErr

        self.session = apns.Session()
        self.con = session.get_connection(config.get("connection"),
                                          cert_file=config.get("cert_file"),
                                          key_file=config.get("key_file"))
        self.defaultTitle = config.get("default_title", self.defaultTitle)
        self.defaultBody = config.get("default_body", self.defaultBody)
        self.storage = config.storage
        log.msg("Starting APNs bridge")

    def send(self, uaid, version, data, connectInfo):
        if connectInfo.get("token") is None:
            raise MissingTokenErr

        srv = apns.APNS(self.con)
        message = apns.Message(
                payload={
                    "alert": connectInfo.get("title", self.defaultTitle),
                    "content_available": 1,

                [connectInfo.get("token")],
                alert=connectInfo.get("title",
                                      self.defaultTitle),
                extra={"Msg": data, "Version": version})

        return self._transmit(srv, message)

    def _transmit(self, srv, message, iter=0):
        if iter > self.maxIter:
            return False
        try:
            result = srv.send(message)
        except Exception, e:
            log.err("Unable to send ANPs message, %s", e)
            return False

        if result.needs_retry():
            self.backoffDelay(1000)
            self.backoff = max(self.backoff + (random.rand(0, 256) * 1000),
                               MaxBackoff)
        return self._send(srv, message.retry(), iter+1)


    def checkFeedback(self):
        if self.storage is None:
            return
        srv = apns.APNS(self.con)
        for item, time in srv.feedback():
            self.storage.byToken("DELETE", item)


def main():
    """ Main commment """


main()

