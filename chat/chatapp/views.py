from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest
)
from django.core.exceptions import SuspiciousOperation

import simplejson

import queue

class JSONResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        content = simplejson.dumps(content)
        kwargs['content_type'] = 'application/json'
        return  super(JSONResponse, self).__init__(content, *args, **kwargs)

class JSONResponseBadRequest(JSONResponse, HttpResponseBadRequest):
    pass

@csrf_exempt
def home(request, *args, **kwargs):
    if request.is_ajax():
        return ajax_handler(request, *args, **kwargs)
    return render(request, 'chat.html', kwargs)

def ajax_handler(request, *args, **kwargs):
    try:
        json_request = simplejson.loads(request.POST.get('request'))
    except simplejson.JSONDecodeError:
        return HttpResponseForbidden()
    try:
        subscriber = json_request['subscriber']
    except KeyError:
        return HttpResponseForbidden()

    if not subscriber:
        return JSONResponseBadRequest({'success': False})

    timeout = json_request.get('timeout', 30)
    data = json_request.get('data')
    command = json_request.get('command')

    if command not in ('submit', 'update'):
        return JSONResponseBadRequest({'success': False, 'error': "unknown command"})

    if command == 'submit':
        queue.send_message(subscriber=subscriber, message=simplejson.dumps(data))
        return JSONResponse({'success': True})

    if command == 'update':
        try:
            resp = queue.wait_message(subscriber=subscriber, block=True, timeout=timeout)
            if resp[0] != subscriber:
                raise SuspiciousOperation("Subscriber does not match returned message subscriber:%s:%s", resp, subscriber)
            resp = resp[1]
        except TypeError:
            resp = None
        return JSONResponse({
            'success': resp is not None,
            'data': (resp != None) and simplejson.loads(resp) or None,
            'timeout': resp is None,
        })
    return HttpResponseForbidden()
