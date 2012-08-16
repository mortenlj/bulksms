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

import supybot.conf as conf
from supybot.test import *

# Work around windows not having good enough precision in timer
conf.supybot.protocols.irc.throttleTime.setValue(-1.0)

root_config = conf.supybot.plugins.BulkSMS

def set_key(config, key, value):
    config["supybot.plugins.BulkSMS." + key] = value

def build_config(custom_config=None):
    config = {}
    set_key(config, "api.username", "username")
    set_key(config, "api.password", "password")
    set_key(config, "phonebook.username", "username") # Must be set to real username for test to work
    set_key(config, "phonebook.password", "password") # Must be set to real password for test to work
    set_key(config, "isTesting", True)
    set_key(config, "isTesting.failing", False)
    if custom_config:
        for key in custom_config.keys():
            set_key(config, key, custom_config[key])
    return config

class BulkSMSDefenceTestCase(ChannelPluginTestCase):
    plugins = ('BulkSMS',)
    config = build_config()
    channel = "#emergency_channel"

    def setUp(self):
        super(BulkSMSDefenceTestCase, self).setUp()
        self.plugin = self.irc.getCallback("BulkSMS")
        from db import Database
        self.plugin.database = Database("sqlite://")

    def testNonExistingNick(self):
        self.assertErrorMessage("sms Nobody This is a test", "Unable to find Nobody in phone book")

    def testSuccessfulSend(self):
        self.getMsg("map #emergency_channel emergency")
        self.assertResponse("sms Epcylon This is a test", "SMS sent successfully to Epcylon")

    def testFailedSend(self):
        self.getMsg("map #emergency_channel emergency")
        try:
            root_config.isTesting.failing.setValue(True)
            self.assertErrorMessage("sms Epcylon This is a test", "Unable to send SMS: 22")
        finally:
            root_config.isTesting.failing.setValue(False)

    def testNotAllowedSend(self):
        self.assertErrorMessage("sms Epcylon This is a test", "Epcylon does not wish to receive SMS")

    def testMapUnMap(self):
        self.getMsg("map #emergency_channel emergency")
        self.assertResponse("sms Epcylon This is a test", "SMS sent successfully to Epcylon")
        self.getMsg("unmap #emergency_channel emergency")
        self.assertErrorMessage("sms Epcylon This is a test", "Epcylon does not wish to receive SMS")

    def assertErrorMessage(self, query, error_message):
        m = self.getMsg(query)
        self.failUnless(m.args[1].startswith('Error: ' + error_message),
                        '%r did not give correct error message: %s' % (query, m.args[1]))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
