#!/usr/bin/env python
# -*- coding: utf-8

class PhoneBook(object):
    """Look up name or number and get the other back.

    Uses a backend webservice to get the information.
    TODO: Implement
    """
    def get_number(self, name):
        if name == "Somebody":
            return "4792491982"
        else:
            return None

    def get_name(self, number):
        return "Epcylon"

if __name__ == "__main__":
    pass
