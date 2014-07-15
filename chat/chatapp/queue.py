from __future__ import absolute_import
import six

import gevent
import zmq.green as zmq

from django.conf import settings
from django.utils.encoding import force_bytes

if six.PY3:
    import queue
else:
    import Queue as queue

__all__ = ['Broadcaster', 'runserver', 'wait_message', 'send_message']

class Broadcaster(object):
    def __init__(self, name, *args, **kwargs):
        self.context = zmq.Context()
        #Broadcast socket for client to subscribe to
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_sock.bind(settings.ZMQ_PUB_ADDRESS)
        
        #Socket to receive messages on so that a client can connect and broadcast to all listeners
        self.recv_sock = self.context.socket(zmq.ROUTER)
        self.recv_sock.bind(settings.ZMQ_SUB_ADDRESS)
        self.quit_queue = queue.Queue()
        self.worker = None
        
        self.poller = zmq.Poller()
        self.poller.register(self.recv_sock, zmq.POLLIN)
        self.poller.register(self.pub_sock, zmq.POLLIN)

    def _handle_next_msg(self):
        socks = dict(self.poller.poll())
        
        if socks.get(self.recv_sock) == zmq.POLLIN:
            self.pub_sock.send_multipart(self.recv_sock.recv_multipart()[1:])
        if socks.get(self.pub_sock) == zmq.POLLIN:
            self.recv_sock.send_multipart(self.pub_sock.recv_multipart()[1:])

    def _worker_thread(self):
        from time import sleep
        import uuid
        print("zmq worker thread starting...")
        while True:
            self._handle_next_msg()
    
    def start(self):
        self._worker_thread()
    
    def stop(self):
        self.quit_queue.put(1)

def runserver(name):
    server = Broadcaster(name)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Exiting...")

def wait_message(subscriber='', block=True, timeout=10):
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(settings.ZMQ_PUB_ADDRESS)
    socket.setsockopt(zmq.SUBSCRIBE, force_bytes(subscriber))
    try:
        c = gevent.spawn(socket.recv_multipart)
        return c.get(block, timeout)
    except gevent.Timeout:
        return None
    finally:
        c.kill()
        socket.close()
        context.destroy()

def send_message(subscriber='', message=''):
    context = zmq.Context()
    
    socket = context.socket(zmq.XREQ)
    socket.connect(settings.ZMQ_SUB_ADDRESS)
    socket.send_multipart([force_bytes(subscriber), force_bytes(message)])
    
    socket.close()
    context.destroy()

