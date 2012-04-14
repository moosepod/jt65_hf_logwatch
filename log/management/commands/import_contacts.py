from django.core.management.base import BaseCommand, CommandError

import datetime
from adif import ADIFParser
from log.models import Contact

class Command(BaseCommand):
    help = 'Import contacts from the ADIF file at the provided path'

    def handle(self, *args, **options):
		f = open('/tmp/contacts.adif')
		d = f.read()
		p = ADIFParser(d)
		r = p.next_record()
		while r.call:
			if r.mode == 'JT65':
				qso_date = datetime.datetime.strptime(r.qso_date,'%Y%m%d')
				contact, created = Contact.objects.get_or_create(
					when = qso_date,
					callsign=r.call,
					band=r.band
				)
				if created: print 'Added',contact
				
			r = p.next_record()
			
		

