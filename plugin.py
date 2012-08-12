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

from supybot.commands import wrap
import supybot.conf as conf
import supybot.callbacks as callbacks

from .local.phonebook import PhoneBook
from .local.bulksms import API, TestAlways, StatusError

def test_always():
    root_config = conf.supybot.plugins.BulkSMS
    if root_config.isTesting():
        if root_config.isTesting.failing():
            return TestAlways.FAIL
        return TestAlways.SUCCEED
    return TestAlways.NO


def channel_to_preferences(chan):
    mapping = conf.supybot.plugins.BulkSMS.mapping()
    return mapping.get(chan, [])

class BulkSMS(callbacks.Plugin):
    """To send a SMS, use the sms command, supplying the nick of the user as first
    parameter. The rest of the line will be sent to the registered phone number of
    that user. Your nick will be appended to the end of the message."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(BulkSMS, self)
        super(BulkSMS, self).__init__(irc)
        self.phone_book = PhoneBook()
        root_config = conf.supybot.plugins.BulkSMS
        self.api = API(root_config.username(), root_config.password())

    def sms(self, irc, msg, args, chan, nick, message):
        """<nick> <message>

        Send an SMS to <nick> with the <message>, with your nick appended to the end
        """
        contact = self.phone_book.get(nick)
        if not contact:
            irc.error("Unable to find %s in phone book" % nick)
            return
        if not contact.number:
            irc.error("%s hasn't registered a phone number in the phone book" % nick)
            return
        preferences = channel_to_preferences(chan)
        if not any((contact.has_preference(preference) for preference in preferences)):
            irc.error("%s does not wish to receive SMS from %s" % (nick, chan))
            return
        sms = "%s -- %s" % (message, msg.nick)
        try:
            self.api.send_sms(sms, contact.number, test_always())
        except StatusError as e:
            irc.error("Unable to send SMS: %s" % str(e))
        else:
            irc.reply("SMS sent successfully to %s" % nick)
    sms = wrap(sms, ["public", "channel", "nick", "text"])

Class = BulkSMS


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
