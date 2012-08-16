#!/usr/bin/env python
# -*- coding: utf-8
import requests

class TestAlways(object):
    NO = 0
    SUCCEED = 1
    FAIL = 2

    @staticmethod
    def to_param(value):
        if value == TestAlways.SUCCEED:
            return {"test_always_succeed": 1}
        if value == TestAlways.FAIL:
            return {"test_always_fail": 1}
        return {}

class APIError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return self.description

class UserError(APIError):
    pass

class ConnectionError(APIError):
    pass

class StatusError(APIError):
    def __init__(self, status_code, description):
        super(StatusError, self).__init__("%d - %s" % (status_code, description))
        self.status_code = status_code

def parse_status_response(response):
    parts = response.split("|")
    return int(parts[0]), parts[1]

class API(object):
    """API to bulksms.com
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def send_sms(self, message, msisdn, source_id, test_always=TestAlways.NO):
        if len(message) > 160:
            raise UserError("Message is more than 160 characters long")
        post_data = {
            "username": self.username,
            "password": self.password,
            "message": message,
            "msisdn": msisdn,
            "sender": "HowlingRain",
            "routing_group": 2,
            "source_id": source_id,
            "repliable": 0,
        }
        post_data.update(TestAlways.to_param(test_always))
        try:
            r = requests.post("http://bulksms.vsms.net:5567/eapi/submission/send_sms/2/2.0", data=post_data)
            r.raise_for_status()
        except (requests.exceptions.RequestException, IOError) as e:
            raise ConnectionError(str(e))
        response = r.text
        if not response.startswith("0"):
            status_code, description = parse_status_response(response)
            raise StatusError(status_code, description)

if __name__ == "__main__":
    bulksms = API("username", "password")
    bulksms.send_sms("This is a test", "4792491982", "Development", TestAlways.SUCCEED)
