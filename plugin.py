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
import os
from threading import Lock

from supybot.commands import wrap
import supybot.conf as conf
import supybot.callbacks as callbacks

from db import Database
from phonebook import PhoneBook, PhoneBookError
from bulksms import API, TestAlways, APIError

def test_always():
    root_config = conf.supybot.plugins.BulkSMS
    if root_config.isTesting():
        if root_config.isTesting.failing():
            return TestAlways.FAIL
        return TestAlways.SUCCEED
    return TestAlways.NO


class BulkSMS(callbacks.Plugin):
    """To send a SMS, use the sms command, supplying the nick of the user as first
    parameter. The rest of the line will be sent to the registered phone number of
    that user. Your nick will be appended to the end of the message."""
    threaded = True

    def __init__(self, irc):
        super(BulkSMS, self).__init__(irc)
        self.database = None
        self.phone_book = None
        self.api = None
        self.init_lock = Lock()

    def die(self):
        if self.database:
            self.database.close()
        if hasattr(self, "__parent"):
            self.__parent.die()

    def sms(self, irc, msg, args, chan, nick, message):
        """<nick> <message>

        Send an SMS to <nick> with the <message>, with your nick appended to the end
        """
        self._lazy_init()
        contact, error_msg = self._get_contact(irc, nick)
        if error_msg:
            self.log.error("Error when getting contact information from phonebook")
            irc.error(error_msg)
            return
        error_msg = self._check_preference(chan, contact, nick)
        if error_msg:
            self.log.error("Error when checking preferences")
            irc.error(error_msg)
            return
        self._send_message(contact, irc, message, msg, nick)
    sms = wrap(sms, ["public", "channel", "nick", "text"])

    def _lazy_init(self):
        with self.init_lock:
            if not self.database:
                self._lazy_init_database()
            if not self.phone_book:
                self._lazy_init_phone_book()
            if not self.api:
                self._lazy_init_api()

    def _lazy_init_database(self):
        data_dir = conf.supybot.directories.data()
        plugin_data_dir = os.path.join(data_dir, "BulkSMS")
        if not os.path.exists(plugin_data_dir):
            os.makedirs(plugin_data_dir)
        db_path = os.path.abspath(os.path.join(plugin_data_dir, "db.sqlite"))
        db_url = "sqlite:///" + db_path
        self.log.debug("Opening database-URL: %r" % db_url)
        self.database = Database(db_url)

    def _lazy_init_phone_book(self):
        root_config = conf.supybot.plugins.BulkSMS
        self.phone_book = PhoneBook(root_config.phonebook.username(), root_config.phonebook.password())

    def _lazy_init_api(self):
        root_config = conf.supybot.plugins.BulkSMS
        self.api = API(root_config.api.username(), root_config.api.password())

    def _get_contact(self, irc, nick):
        error_msg = None
        contact = None
        try:
            contact = self.phone_book.get(nick)
        except PhoneBookError as e:
            error_msg = "Error while looking up nick: %s" % str(e)
        if not contact:
            error_msg = "Unable to find %s in phone book" % nick
        elif not contact.number:
            error_msg = "%s hasn't registered a phone number in the phone book" % nick
        return contact, error_msg

    def _check_preference(self, chan, contact, nick):
        mappings = self.database.get_mappings(chan)
        if not any((contact.has_preference(mapping.preference) for mapping in mappings)):
            return "%s does not wish to receive SMS from %s" % (nick, chan)

    def _send_message(self, contact, irc, message, msg, nick):
        sms = "%s -- %s" % (message, msg.nick)
        try:
            self.log.info("Sending SMS to %s: %r" % (contact, sms))
            self.api.send_sms(sms, contact.number, msg.nick, test_always())
        except APIError as e:
            self.log.error("Exception caught when sending SMS")
            irc.error("Unable to send SMS: %s" % str(e))
        else:
            irc.reply("SMS sent successfully to %s" % nick)

    def map(self, irc, msg, args, chan, preference):
        """<channel> <preference>

        Map preference to channel
        """
        self._lazy_init()
        if not self.database.has_mapping(chan, preference):
            self.database.add_mapping(chan, preference)
        irc.reply("OK")
    map = wrap(map, ["admin", "channel", "somethingWithoutSpaces"])

    def unmap(self, irc, msg, args, chan, preference):
        """<channel> <preference>

        Remove mapping of preference to channel
        """
        self._lazy_init()
        if self.database.has_mapping(chan, preference):
            self.database.remove_mapping(chan, preference)
        irc.reply("OK")
    unmap = wrap(unmap, ["admin", "channel", "somethingWithoutSpaces"])

Class = BulkSMS


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
