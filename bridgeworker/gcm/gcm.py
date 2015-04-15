# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gcmclient

from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.python import log
from twisted.spread import pb


class GCMMessageErr(Exception):

    def __init(self, uaid, reg_id, msg=""):
        self.uaid = uaid
        self.reg_id = reg_id
        self.msg = msg

    def __str__(self):
        return "GCM Message Error for uaid:%s as %s, err: %s" % (
            self.uaid,
            self.reg_id,
            self.msg,
        )


class GCMBridge(pb.Root):
    gcm = None
    ttl = 60
    dryRun = 0
    collapseKey = "simplepush"
    storage = None

    def __init__(self, config):
        self.ttl = config.get("ttl", 60)
        self.dryRun = config.get("dryrun", False)
        self.collapseKey = config.get("collapseKey", "simplepush")
        self.gcm = gcmclient.GCM(config.get("apikey"))
        self.storage = config.get("storage", None)
        self.waitTime = config.get("retrydelay", 120)
        self.jitterTime = config.get("retryjitter", 60)
        #log.msg("Starting GCM bridge...")

    def _send(self, uaid, payload, connectInfo, tries=0):
        if tries > 4:
            raise GCMMessageErr(uaid, connectInfo["token"],
                                "Too many retries")
        try:
            reply = self.gcm.send(payload)
        except gcmclient.GCMAuthenticationError, e:
            log.err(e)
            raise
        # handle reply content
        if self.storage is not None:
            # acks:
            # for reg_id, msg_id in reply.success.items():
            # updates
            for old_id, new_id in reply.canonical.items():
                connectInfo["token"] = new_id
                self.storage.store(uaid, connectInfo)
            # uninstall:
            for reg_id in reply.not_registered:
                self.storage.remove(uaid, connectInfo)
        # naks:
        if reply.failed.items().length > 0:
            log.err("Messages failed to be delivered.")
            raise GCMMessageErr(uaid,
                                connectInfo["token"],
                                "Message failed delivery")
        # retries:
        if reply.needs_retry():
            jitterTime = self.randrange(0 - self.jitterTime, self.jitterTime)
            reactor.callLater(jitterTime, self.send,
                              reply.retry(), uaid, connectInfo,
                              tries + 1)

    def remote_ping(self, uaid, version, data, connectInfo):
        try:
            if connectInfo.get("type").lower() != "gcm":
                log.err("connect info isn't gcm")
                return False
            if connectInfo.get("token") is None:
                log.err("connect info missing 'token'")
                return False

            payload = self.gcm.JSONMessage(
                registration_ids=[connectInfo.get("token")],
                collapse_key=self.collapseKey,
                time_to_live=self.ttl,
                dry_run=self.dryRun,
                data={"Msg": data,
                      "Version": version}
            )
            d = deferToThread(self._send, uaid, payload, connectInfo)
            ## TODO: Do we need a callback?
            d.addErrback(log.err)
        except ValueError, e:
            log.err("GCM returned error %s" % e.args[0])
            raise GCMMessageErr(uaid,
                                connectInfo.get("token", "MISSING"),
                                e.args[0])
        except Exception, e:
            log.err("Unhandled exception caught %s" % e)
            raise

    def remote_status(self):
        return "OK"

    def remote_terminate(self):
        reactor.callLater(0.5, reactor.stop)
        log.msg("Terminating...")


