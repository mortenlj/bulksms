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
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import   something

    BulkSMS = conf.registerPlugin('BulkSMS', True)
    username = something("Username for the bulksms.com API?")
    BulkSMS.api.username.setValue(username)
    password = something("Password for the bulksms.com API?")
    BulkSMS.api.password.setValue(password)
    username = something("Username for the phonebook?")
    BulkSMS.phonebook.username.setValue(username)
    password = something("Password for the phonebook?")
    BulkSMS.phonebook.password.setValue(password)

BulkSMS = conf.registerPlugin('BulkSMS')
# This is where your configuration variables (if any) should go.  For example:
conf.registerGroup(BulkSMS, "api")
conf.registerGlobalValue(BulkSMS.api, "username",
    registry.String("", "Username for the bulksms.com API"))
conf.registerGlobalValue(BulkSMS.api, "password",
    registry.String("", "Password for the bulksms.com API"))
conf.registerGroup(BulkSMS, "phonebook")
conf.registerGlobalValue(BulkSMS.phonebook, "username",
    registry.String("", "Username for the phonebook"))
conf.registerGlobalValue(BulkSMS.phonebook, "password",
    registry.String("", "Password for the phonebook"))

# These settings are useful when testing the bot, or running unittests
conf.registerGlobalValue(BulkSMS, "isTesting",
    registry.Boolean(False, "Don't send any SMS, just use test method in API"))
conf.registerGlobalValue(BulkSMS.isTesting, "failing",
    registry.Boolean(False, "Should test requests fail or succeed"))
    
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
