from django.db import models

class Entry(models.Model):
	when = models.DateTimeField()
	frequency = models.DecimalField(max_digits=10,decimal_places=4)
	sync = models.PositiveIntegerField(null=True,blank=True)
	dt = models.DecimalField(max_digits=4,decimal_places=1,null=True,blank=True)
	db = models.IntegerField(null=True,blank=True)
	df = models.IntegerField(null=True,blank=True)
	decoder = models.CharField(max_length=1)
	exchange = models.CharField(max_length=13)
	tx = models.BooleanField()

	def __unicode__(self):
		return u'%s - %s' % (self.when,self.exchange)
