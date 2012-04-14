from django.core.management.base import BaseCommand, CommandError

from time import sleep
from log.models import JT65LogFile

class Command(BaseCommand):
    help = 'Start an endless loop to load any changed logfile entries from JT65-hf'

    def handle(self, *args, **options):
	try:
		lf = JT65LogFile.objects.all().order_by('-id')[0]
	except IndexError:
		print 'No log file configured in database. Please use the admin to configure.'
		return

	print 'Loading from %s' % lf.path

	# This is a terribly inefficient way to do things, but since I have a dedicated "ham" computer for
	# this process, it is acceptable
	while True:
		if lf.load():
			print ' Found new data, loading'
		sleep(1)
		

