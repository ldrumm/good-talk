from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden

import simplejson

import queue

class JSONResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        content = simplejson.dumps(content)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, *args, **kwargs)

@csrf_exempt
def home(request, *args, **kwargs):
    if request.is_ajax():
        return ajax_handler(request, *args, **kwargs)
    return render(request, 'chat.html', kwargs)

def ajax_handler(request, *args, **kwargs):
    try:
        d = simplejson.loads(request.POST.get('request'))
    except simplejson.JSONDecodeError:
        return HttpResponseForbidden()
    try:
        subscriber = d['subscriber']
    except KeyError:
        return HttpResponseForbidden()
    timeout = d.get('timeout', 30)
    data = d.get('data')
    
    if d.get('command') == 'submit':
        queue.send_message(subscriber=subscriber, message=simplejson.dumps(data))
        return JSONResponse({'success': True})
    
    if d.get('command') == 'update':
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
