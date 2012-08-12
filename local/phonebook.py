#!/usr/bin/env python
# -*- coding: utf-8

class Contact(object):
    def __init__(self, nick, number, preferences):
        self.nick = nick
        self.number = number
        self.preferences = preferences

    def has_preference(self, preference):
        return self.preferences[preference]

class PhoneBook(object):
    """Look up name or number and get contact back.

    Uses a backend webservice to get the information.
    TODO: Implement
    """
    def get(self, query):
        if query == "Somebody":
            return Contact("Somebody", "4792491982", {
                "defence": True,
                "emergency": True
            })
        else:
            return None

if __name__ == "__main__":
    pass
