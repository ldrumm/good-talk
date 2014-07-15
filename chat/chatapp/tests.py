from django.test import TestCase
from django.test.client import RequestFactory
# Create your tests here.
from views import JSONResponse
BASE_REQUEST_DICT = {'request':{
            "command":"submit",
            "subscriber":"",
            "data":{
                "ciphertext":""
                ,"iv":""
                ,"salt":""
            },
            "timeout":50
        }}

class RegressionTests(TestCase):

    def test_issue_1_returns_bad_request(self):
        """ An empty subscriber field is not allowed and should not be processed """
        from django.http import HttpResponseForbidden
        from views import ajax_handler, JSONResponseBadRequest
        bad_request = RequestFactory().post('/', {'request':'''{
            "command":"submit",
            "subscriber":"",
            "data":{
                "ciphertext":""
                ,"iv":""
                ,"salt":""
            },
            "timeout":50
        }'''})

        response = ajax_handler(bad_request)
        self.assertIsInstance(response, (HttpResponseForbidden, JSONResponseBadRequest))

class HttpClassTests(TestCase):

    def test_json_response_headers(self):
        #Make sure mime is corrent Per RFC 4627
        response = JSONResponse({})
        self.assertEqual(response['content-type'], 'application/json')

    def test_json_response_rountrip(self):
        from django.utils.crypto import get_random_string
        import simplejson
        fixture = {get_random_string():get_random_string() for x in range(1000)}

        response = JSONResponse(fixture)
        deserialised = simplejson.loads(response.content)
        self.assertEqual(sorted(fixture.keys()), sorted(deserialised.keys()))
        for x in fixture.keys():
            self.assertEqual(fixture[x], deserialised[x])

class AJAXTests(TestCase):
    def test_bad_command_fails(self):
        from views import ajax_handler
        from django.utils.crypto import get_random_string
        bad_request = RequestFactory().post('/', {'request':'''{
            "command":"%s",
            "subscriber":"",
            "data":{
                "ciphertext":""
                ,"iv":""
                ,"salt":""
            },
            "timeout":50
        }''' % get_random_string()}
        )
        response = ajax_handler(bad_request)
        self.assertNotEqual(response.status_code, 200)
