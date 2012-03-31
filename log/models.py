import re

from django.db import models

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
