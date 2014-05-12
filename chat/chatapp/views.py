from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden

import simplejson


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
    if d.get('cmd') == 'submit':
        resp = post_message(d.get('data'), *args, **kwargs)
        return HttpResponse(
            simplejson.dumps({
                'success': True,
            })
        )
    if d.get('cmd') == 'update':
        resp = long_poll_update_status(d.get('data'), *args, **kwargs)
        return HttpResponse(
            simplejson.dumps({
                'success': resp is not None,
                'msg':resp,
                'timeout':resp is None,
            })
        )
    return HttpResponseForbidden()

def post_message(data, *args, **kwargs):
    from queue import send_message
    send_message('', data)

def long_poll_update_status(data, timeout=20, **kwargs):
    from queue import wait_message as get_message
    from django.utils.html import escape
    from django.utils.safestring import mark_for_escaping
    timeout = timeout > 20 and 20 or timeout
    timeout = timeout > 0 and timeout or 20
    try:
        msg = str(get_message(timeout=timeout)[0])
    except TypeError:
        return None
    return escape(msg)
