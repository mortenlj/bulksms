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

def set_key(config, key, value):
    config["supybot.plugins.BulkSMS." + key] = value

def build_config(custom_config=None):
    config = {}
    set_key(config, "isTesting", True)
    set_key(config, "isTesting.failing", False)
    set_key(config, "allowInAnyChannel", False)
    set_key(config, "mapping", {
        "first": ["#first_a", "#first_b"],
        "second": ["#second_a", "#second_b"]
        })
    if custom_config:
        for key in custom_config.keys():
            set_key(config, key, custom_config[key])
    return config

class BulkSMSTestCase(ChannelPluginTestCase):
    plugins = ('BulkSMS',)
    config = build_config()


class BulkSMSAnyChannelTestCase(ChannelPluginTestCase):
    plugins = ('BulkSMS',)
    config = build_config({"allowInAnyChannel": True})

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
