import csv
import datetime

from log.models import Entry

def import_log(filename):
	f = open(filename)
	r = csv.reader(f)
	for l in r:
		print l
		if l[0] == 'Date': continue
		if len(l) < 10: continue
		date, time, qrg, sync, db, dt, df, decoder, exchange = l[0:9]
		when = datetime.datetime.strptime('%s %s' % (date,time),'%Y-%m-%d %H:%M')
		try:
			Entry.objects.get(when=when,exchange=exchange)	
		except Entry.DoesNotExist:
			Entry.objects.create(when=when,
					frequency=qrg,
					sync=sync,
					db=db,
					dt=dt,
					df=df,
					decoder=decoder,
					exchange=exchange)
