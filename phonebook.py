#!/usr/bin/env python
# -*- coding: utf-8

import re
import requests

from bs4 import BeautifulSoup

class PhoneBookError(Exception):
    def __init__(self, description, *args, **kwargs):
        super(PhoneBookError, self).__init__(*args, **kwargs)
        self.description = description

    def __str__(self):
        return self.description

CLEAN_NUMBER_PATTERN = re.compile("[-.+ ]")

class Contact(object):
    def __init__(self, nick, number, preferences):
        self.nick = nick
        self.number = Contact.normalize(number)
        self.preferences = preferences

    def has_preference(self, preference):
        return self.preferences[preference]

    def __str__(self):
        return "%s (%s) - %r" % (self.nick, self.number, self.preferences)

    @staticmethod
    def normalize(number):
        number = CLEAN_NUMBER_PATTERN.sub(u"", number)
        if number.startswith(u"00"):
            number = number[2:]
        return number

class PhoneBook(object):
    """Look up name or number and get contact back.

    Uses a backend webservice to get the information.
    """
    phonebook_url = "https://arby.howlingrain.co.uk/api.php"
    login_url = "https://forum.howlingrain.co.uk/ucp.php"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session(verify=False)
        self.login()

    def get(self, query, should_retry=True):
        params = {
            "cmd": "contact",
            "q[]": query
        }
        r = self.session.get(self.phonebook_url, params=params, allow_redirects=False)
        if r.status_code != requests.codes.ok:
            if should_retry:
                self.login()
                return self.get(query, False)
            else:
                raise PhoneBookError("Unable to get data from phone book (%d)" % r.status_code)
        json_data = r.json
        if json_data and u"results" in json_data:
            print json_data
            contact_data = json_data[u"results"]
            print contact_data
            if query in contact_data and contact_data[query]:
                name = PhoneBook.extract(contact_data[query], u"name")
                number = PhoneBook.extract(contact_data[query], u"number")
                pref = PhoneBook.extract(contact_data[query], u"pref")
                return Contact(name, number, pref)
        return None

    def login(self):
        sid = self.load_login_page()
        self.perform_login(sid)

    def perform_login(self, sid):
        params = {"mode": "login"}
        post_data = {
            "username": self.username,
            "password": self.password,
            "sid": sid,
            "login": "Login",
            "autologin": "on"
        }
        try:
            r = self.session.post(self.login_url, params=params, data=post_data)
            r.raise_for_status()
        except (requests.exceptions.RequestException, IOError) as e:
            raise PhoneBookError("Unable to log in: %s" % str(e))
        html = BeautifulSoup(r.text)
        error = html.find(u"span", attrs={u"class": u"error"})
        if error:
            raise PhoneBookError("Error logging in: %s" % error.string)

    def load_login_page(self):
        params = {"mode":"login"}
        try:
            r = self.session.get(self.login_url, params=params)
            r.raise_for_status()
        except (requests.exceptions.RequestException, IOError) as e:
            raise PhoneBookError("Unable to log in: %s" % str(e))
        html = BeautifulSoup(r.text)
        sid_input = html.find(u"input", attrs={u"type":u"hidden", u"name": u"sid"})
        return sid_input[u"value"]

    @staticmethod
    def extract(contact_data, key):
        try:
            return contact_data[key]
        except KeyError:
            pass
        return ""


if __name__ == "__main__":
    pb = PhoneBook("username", "password")
    print "Will", pb.get("Will")
    print "Epcylon", pb.get("Epcylon")
    print "ASDFASDF", pb.get("ASDFASDF")
