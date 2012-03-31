import csv
import datetime

# Row is: date, time, frequency, sync, db, dt, df, decoder, exchange
def import_row(row):
	if not row: return None
	if len(row) < 9: return None
	if row[0] == 'Date': return
	
	date, time, qrg, sync, db, dt, df, decoder, exchange = row[0:9]

	when = datetime.datetime.strptime('%s %s UTC' % (date,time),'%Y-%m-%d %H:%M %Z')
	from log.models import Entry
        try:
        	e = Entry.objects.get(when=when,exchange=exchange)
        except Entry.DoesNotExist:
                e = Entry.objects.create(when=when,
                                     frequency=qrg,
                                     sync=sync,
                                     db=db,
                                     dt=dt,
                                     df=df,
                                     decoder=decoder,
                                     exchange=exchange)

	return e

	
	

