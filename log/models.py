import re
import os
import csv

from django.db import models
from log import import_row

class JT65LogFile(models.Model):
	path = models.CharField(max_length=1000,unique=True,help_text='Absolute path to log file')
	file_size = models.PositiveIntegerField()

	def file_changed(self):
		newsize = os.path.getsize(self.path)
		if not self.file_size:
			return True

		return newsize != self.file_size

	def load(self):
		if self.file_changed():
			new_size = os.path.getsize(self.path)
			start_at = self.file_size
			if new_size < self.file_size: start_at = 0
				
			with open(self.path) as f:
				f.seek(start_at)
				r = csv.reader(f)
				for l in r:
					print 'Importing %s' % l[-2]
					import_row(l)
	
			self.store_size()
			return True
		return False
	
	def store_size(self):
		self.file_size = os.path.getsize(self.path)
		self.save()

	def __unicode__(self):
		return self.path

	class Meta:
		verbose_name = 'JT65LogFile'

class Entry(models.Model):
	GRIDSQUARE_RE = re.compile('\w\w\d\d')
	SIGNAL_RE     = re.compile('R?-\d+')

	when = models.DateTimeField()
	frequency = models.DecimalField(max_digits=10,decimal_places=4)
	sync = models.PositiveIntegerField(null=True,blank=True)
	dt = models.DecimalField(max_digits=4,decimal_places=1,null=True,blank=True)
	db = models.IntegerField(null=True,blank=True)
	df = models.IntegerField(null=True,blank=True)
	decoder = models.CharField(max_length=1)
	exchange = models.CharField(max_length=13)
	tx = models.BooleanField()

	callsign = models.CharField(max_length=10,null=True,blank=True)

	def save(self,*args,**kwargs):
		if self.exchange and not self.callsign:
			self.callsign = self.extract_callsign()

		return super(Entry,self).save(*args,**kwargs)

	def extract_callsign(self):	
		if not self.exchange: return None
		
		parts = self.exchange.split(' ')
		if len(parts) == 3:
			if parts[0]  == 'CQ' : return parts[1] # CQ KC2ZUF EM09
			if parts[2]  == 'RRR': return parts[1]
			if Entry.GRIDSQUARE_RE.match(parts[2]): return parts[1]
			if Entry.SIGNAL_RE.match(parts[2]): return parts[1]

		return None

	def __unicode__(self):
		return u'%s - %s' % (self.when,self.exchange)

	class Meta:
		verbose_name_plural = 'Entries'

# Note that we assume a JT65 mode here. This is not meant
# to be a full logger, just to check for previous contacts
class Contact(models.Model):
	when = models.DateField()
	callsign = models.CharField(max_length=100)
	band = models.CharField(max_length=10)
	
	def __unicode__(self):
		return u'%s : %s' % (self.callsign, self.when)
	
