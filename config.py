###
# Copyright (c) 2012, Morten Lied Johansen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from collections import defaultdict
from json import dumps, loads

import supybot.conf as conf
import supybot.registry as registry

class JsonValue(registry.Value):
    """Any value that can be serialized to JSON. Probably hard to work with manually.
    """

    def serialize(self):
        json_value = dumps(self())
        return json_value.replace('\\', '\\\\')

    def set(self, json_value):
        s = loads(json_value)
        self.setValue(s)


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    BulkSMS = conf.registerPlugin('BulkSMS', True)
    username = something("Username for the bulksms.com API?")
    BulkSMS.username.setValue(username)
    password = something("Password for the bulksms.com API?")
    BulkSMS.password.setValue(password)
    pb_url = something("URL to the phonebook service (see README for details)?")
    BulkSMS.phonebook_url.setValue(pb_url)
    if yn("""Do you want to restrict this plugin to only selected channels, mapped
             to contact preferences (see README for details)?""", default=True):
        mapping = defaultdict(list)
        more = True
        while more:
            preference = something("Preference?")
            channel = something("Channel?")
            mapping[preference].append(channel)
            more = yn("Add another channel?", default=True)
        BulkSMS.mapping.setValue(dict(mapping))
    else:
        BulkSMS.allowInAnyChannel.setValue(True)

BulkSMS = conf.registerPlugin('BulkSMS')
# This is where your configuration variables (if any) should go.  For example:
conf.registerGlobalValue(BulkSMS, "allowInAnyChannel",
    registry.Boolean(False, "Allow sending SMS from any channel."))
conf.registerGlobalValue(BulkSMS, "username",
    registry.String("", "Username for the bulksms.com API"))
conf.registerGlobalValue(BulkSMS, "password",
    registry.String("", "Password for the bulksms.com API"))
conf.registerGlobalValue(BulkSMS, "phonebook_url",
    registry.String("", "URL to the phonebook service"))
conf.registerGlobalValue(BulkSMS, "mapping",
    JsonValue({}, "A dictionary mapping preference to a list of channels"))

# These settings are useful when testing the bot, or running unittests
conf.registerGlobalValue(BulkSMS, "isTesting",
    registry.Boolean(False, "Don't send any SMS, just use test method in API"))
conf.registerGlobalValue(BulkSMS.isTesting, "failing",
    registry.Boolean(False, "Should test requests fail or succeed"))
    
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
