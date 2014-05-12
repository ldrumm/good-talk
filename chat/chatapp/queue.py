import zmq.green as zmq
from django.conf import settings
import Queue


class Broadcaster(object):
    def __init__(self, name, *args, **kwargs):
        self.context = zmq.Context()
        #Broadcast socket for client to subscribe to
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_sock.bind(settings.ZMQ_PUB_ADDRESS)
        
        #Socket to receive messages on so that a client can connect and broadcast to all listeners
        self.recv_sock = self.context.socket(zmq.ROUTER)
        self.recv_sock.bind(settings.ZMQ_SUB_ADDRESS)
        self.quit_queue = Queue.Queue()
        self.worker = None
        
        self.poller = zmq.Poller()
        self.poller.register(self.recv_sock, zmq.POLLIN)
        self.poller.register(self.pub_sock, zmq.POLLIN)
   
    def _publish(self, msg):
        socks = dict(self.poller.poll())


    def _handle_next_msg(self):
        socks = dict(self.poller.poll())
        
        if socks.get(self.recv_sock) == zmq.POLLIN:
            self.pub_sock.send_multipart(self.recv_sock.recv_multipart()[1:])
        if socks.get(self.pub_sock) == zmq.POLLIN:
            self.recv_sock.send_multipart(self.pub_sock.recv_multipart()[1:])

    def _worker_thread(self):
        from time import sleep
        import uuid
        print("worker thread starting...")
        while True:
            quit = None
            try:
                quit = self.quit_queue.get_nowait()
                if quit:
                    print "received quit"
                    break
            except Queue.Empty:
                pass
            self._handle_next_msg()
    
    def start(self):
        import threading
        try:
            if self.worker.is_alive():
                raise RuntimeError("message worker thread is already running")
        except AttributeError:
            pass    
            
        self.worker = threading.Thread(target = self._worker_thread, )
        self.worker.run()
        print(worker)
    
    def stop(self):
        self.quit_queue.put(1)
#        try:
#            self.worker.join()
#        except AttributeError:
#            pass

def wait_message(subscriber='', timeout=10, block=True):
    flags = not block and zmq.NOBLOCK or 0
    timeout = timeout and (timeout * 1000) or -1
    context = zmq.Context()
    
    socket = context.socket(zmq.SUB)
    socket.connect(settings.ZMQ_PUB_ADDRESS)
    socket.RCVTIMEO = timeout
    socket.setsockopt(zmq.SUBSCRIBE, subscriber)
    try:
        message = socket.recv_multipart(flags=flags)
        return message
    except zmq.Again:
        return None
    finally:
        socket.close()
        context.destroy()
    

def send_message(message, subscriber=''):
    context = zmq.Context()
    
    socket = context.socket(zmq.XREQ)
    socket.connect(settings.ZMQ_SUB_ADDRESS)
    socket.send_multipart([str(subscriber), str(message)])
    
    socket.close()
    context.destroy()


def runserver():
    server = Broadcaster('none')
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Exiting...")
        
