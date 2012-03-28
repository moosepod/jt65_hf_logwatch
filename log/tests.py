from unittest import TestCase
import datetime

from log.models import Entry

class EntryTests(TestCase):
	def test_unicode(self):
		e = Entry(when=datetime.datetime(2012,1,2,3,4,5),
			  exchange='CQ KC2ZUF')
		self.assertEquals(u'2012-01-02 03:04:05 - CQ KC2ZUF',unicode(e))

