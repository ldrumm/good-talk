from django.core.management.base import BaseCommand, CommandError
from chatapp.queue import runserver

class Command(BaseCommand):
    args = None
    help = 'Run the zmq message server for chat'

    def handle(self, *args, **options):
        
        runserver("ChatApp")
