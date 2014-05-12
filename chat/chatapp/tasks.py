#import celery
#import Queue
#from celery import shared_task
#from celery.exceptions import TimeoutError
#from chat.celery import app
#from django.utils.timezone import now

#@shared_task
#def get_message(queue_name='task-received', timeout=10, limit=1, ):
#    import pdb
#    start = now()
#    print start
#    state = app.events.State()
#    last_result = Queue.Queue()
#    
#    def announce_tasks(event):
#        state.event(event)
#        print "announce_tasks"
#        # task name is sent only with -received event, and state
#        # will keep track of this for us.
##        for x in event.keys():
##            print x,':', event[x]
#        print 'callback', last_result
#        task = app.AsyncResult(event['uuid'])
#        if event.get('name') != 'chatapp.tasks.send_msg':
#            print "NAME IS WRONG %s" % name
#            return
#        task.wait(timeout)
#        print "TASK RESULT:%s" % task.result
#        last_result.put(task.result)
#        return last_result

#    with app.connection() as connection:
#        recv = app.events.Receiver(connection, handlers={
#                queue_name: announce_tasks
#        })
#        while (now() - start).seconds < timeout:
#            try:
#                recv.capture(limit=100, timeout=1, wakeup=True)
#            except Exception as e:
#                pass
#            try:
#                item = last_result.get_nowait()  
#                print item
#                return item
#            except Queue.Empty:
##                    pdb.set_trace()
#                continue
#    return None
#@shared_task
#def send_msg(queue_name, message):
#    print "sending '%s'" %message
#    return message
