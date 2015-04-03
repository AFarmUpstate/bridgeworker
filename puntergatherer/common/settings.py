# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#from x import y


class PGSettings(object):

    def __init__(self,
                 args,
                 **kwargs):
        for key, val in args:
            setattr(self, key, val)
        for key, val in kwargs.items():
            setattr(self, key, val)
