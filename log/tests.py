from unittest import TestCase
import datetime

from log import import_row
from log.models import Entry

class EntryTests(TestCase):
	def test_unicode(self):
		e = Entry(when=datetime.datetime(2012,1,2,3,4,5),
			  exchange='CQ KC2ZUF')
		self.assertEquals(u'2012-01-02 03:04:05 - CQ KC2ZUF',unicode(e))

	def test_save(self):
		e = Entry.objects.create(when=datetime.datetime(2012,1,2,3,4,5),
			  frequency='28.111',
                          exchange='CQ KC2ZUF FN03')
		self.assertEquals('KC2ZUF', e.callsign)

	def test_extract_callsign_none(self):
		e = Entry(exchange=None)
		self.assertFalse(e.extract_callsign())
		e.exchange = ''
		self.assertFalse(e.extract_callsign())

	def test_extract_callsign_invalid(self):
		e = Entry(exchange='73 DIPOLE 10m')
		self.assertFalse(e.extract_callsign())

	def test_extract_callsign_cq(self):
		e = Entry(exchange='CQ KC2ZUF FN03')
		self.assertEquals('KC2ZUF',e.extract_callsign())

	def test_extract_callsign_exchange(self):
		e = Entry(exchange='KC2ZUF W2PE R-14')
		self.assertEquals('W2PE', e.extract_callsign())
		e = Entry(exchange='KC2ZUF W2PE -04')
		self.assertEquals('W2PE', e.extract_callsign())

	def test_extract_callsign_rrr(self):
		e = Entry(exchange='W2PE KC2ZUF RRR')
		self.assertEquals('KC2ZUF',e.extract_callsign())

	def test_extract_loc(self):
		e = Entry(exchange='W2PE KC2ZUF FN03')
		self.assertEquals('KC2ZUF',e.extract_callsign())

class ImporterTests(TestCase):
	def setUp(self):
		Entry.objects.all().delete()		

	def test_empty_row(self):
		self.assertFalse(import_row(None))
		self.assertFalse(import_row([]))
		self.assertFalse(Entry.objects.all().count())

	def test_date_row(self):	
		self.assertFalse(import_row(['Date','Time','Freq','Sync','DB','DT','DF','Decoder','Exchange']))
		self.assertFalse(Entry.objects.all().count())

	def test_import(self):
		e = import_row(['2012-01-02','03:11','28.123','1','-25','-333','1','A','CQ KC2ZUF FN03'])
		self.assertTrue(e)
		self.assertEquals(1,Entry.objects.all().count())
		self.assertEquals(2012,e.when.year)
		self.assertEquals(1,e.when.month)
		self.assertEquals(2,e.when.day)
		self.assertEquals(3,e.when.hour)
		self.assertEquals(11,e.when.minute)
		self.assertEquals('28.123',e.frequency)
		self.assertEquals('1',e.sync)
		self.assertEquals('-25',e.db)
		self.assertEquals('-333',e.dt)
		self.assertEquals('1',e.df)
		self.assertEquals('A',e.decoder)
		self.assertEquals('CQ KC2ZUF FN03',e.exchange)
