#!/usr/bin/env python
# -*- coding: utf-8

class TestAlways(object):
    NO = 0
    SUCCEED = 1
    FAIL = 2

class StatusError(Exception):
    def __init__(self, status_code, description):
        self.status_code = status_code
        self.description = description

    def __str__(self):
        return "%d - %s" % (self.status_code, self.description)

class API(object):
    """API to bulksms.com

    TODO: Implement
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def send_sms(self, message, msisdn, test_always=TestAlways.NO):
        if test_always == TestAlways.FAIL:
            raise StatusError(22, "Internal error")
        return True

if __name__ == "__main__":
    pass
