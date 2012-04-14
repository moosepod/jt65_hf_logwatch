from django.core.cache import cache
from django.db import models

from xml.parsers.expat import ExpatError

import StringIO
import urllib2
import re

import elementtree.ElementTree as ET

### See http://www.qrz.com/XML/current_spec.html for spec
class QRZException(Exception):
	pass

class QRZCredentials(models.Model):
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100)
    
    qrz_url = models.CharField(max_length=255) 
    qrz_agent = models.CharField(max_length=100)

    session_id = models.CharField(max_length=100,null=True,blank=True)

    def lookup_callsign(self,callsign):
		qrz = None
		
		try:	
			if not self.session_id:
				self.login()
	
			if not callsign:
				qrz= QRZRecord()
				qrz.error = 'Missing callsign.'
			else:
				if callsign == 'TESTING' and settings.DEBUG:
					# Some kind of dependency injection would probably work better here, but this is
					# the expedient way to do things
					data = 'asdfa'
				else:
					data = self.get_qrz_data(callsign)
							
				if data:
					qrz = QRZRecord(xml_data=data)

					if qrz.session_timeout:
						self.login()
						data = self.get_qrz_data(callsign)
						qrz = QRZRecord(xml_data=data)
				else:
					qrz = QRZRecord()
					qrz.is_authenticated = False
					qrz.error = 'Unable to connect to QRZ.com'
		except QRZException, e:
			qrz = QRZRecord()
			qrz.error = e.message

		return qrz

    def get_qrz_data(self, callsign):
        key = 'qrz-%s:%s' % (callsign, self.session_id)
        data = cache.get(key)
        if not data:
            data = self.load_url('%s?s=%s;callsign=%s' % (self.qrz_url, self.session_id,callsign))
            # Our parsing code assumes a namespace of www.qrz.com, so fix that here
            data.replace('http://xml.qrz.com','http://www.qrz.com')
            cache.set(key, data)

        return data

    def login(self):
        data = self.load_url('%s?username=%s;password=%s;agent=%s' % (self.qrz_url,self.username,self.password,self.qrz_agent))
        if not data: data = ''
        rx = re.compile('<Key>([^<]*)</Key>')
        m = rx.search(data)
        if not m:
           raise QRZException('Unable to log in to QRZ')

        self.session_id = m.group(1)
        self.save()  

    # @todo add timeout
    def load_url(self, url):
	    print 'Fetching url'
	    usock = urllib2.urlopen(url)
	    data = usock.read()
	    usock.close()
	
	    return data

    def __unicode__(self):
        return self.username
   
    class Meta:
		verbose_name = 'QRZCredentials'
		verbose_name_plural = 'QRZCredentials'

class QRZRecord(object):
    LICENSE_CLASSES = {'G': 'General',
                       'T': 'Technician',
                       'C': 'Club',
                       'E': 'Extra',
                       'N': 'Novice',
                       'A': 'Advanced',
                       }
    def __init__(self, xml_data=None):
        self.error = None
        self.call = None           # call
        self.fname = None          # fname
        self.name = None           # name
        self.addr1 = None          # addr1
        self.addr2 = None          # addr2
        self.state = None          # state 
        self.zip = None            # zip
        self.country = None        # country
        self.lat = None            # lat
        self.lon = None            # lon
        self.grid = None           # grid
        self.county = None         # county
        self.license_class = None  # class
        self.qsl_eqsl = None      # eqsl
        self.is_authenticated = False
        self.qsl_direct = None    # mqsl
        self.qsl_lotw   = None    # lotw
        self.session_timeout = False

        if xml_data:    
            self.load_from_xml(xml_data)
    
    def license_class_expanded(self):
        if not self.license_class:
            return 'Other'

        return QRZRecord.LICENSE_CLASSES.get(self.license_class,self.license_class)

    def is_dx(self):
        if not self.country: 
            return False

        return 'united states' != self.country.lower()

    def find_qrz_value(self, root, tag):
        node = root.find('{http://www.qrz.com}%s' % tag)

        if node == None:
            return None

        return node.text

    def will_direct(self):
	return '1' == self.qsl_direct

    def will_lotw(self):
	return '1' == self.qsl_lotw

    def load_from_xml(self, xml_data):
        try:
            tree = ET.parse(StringIO.StringIO(xml_data))
            doc = tree.getroot()
							
            try:
                session = [n for n in doc.getchildren() if n.tag == '{http://www.qrz.com}Session'][0]
            except IndexError:
                session = None
            
            try:
                callsign = [n for n in doc.getchildren() if n.tag == '{http://www.qrz.com}Callsign'][0]
            except IndexError:
                callsign = None
	    
	    	if not callsign:
				self.is_authenticated = False
                error = self.find_qrz_value(session,'Error')
                if error == 'Session Timeout':
					self.session_timeout = True
     
                if error != 'Invalid session key':
                    self.error = error
            else:
                self.is_authenticated = True
                self.call = self.find_qrz_value(callsign,'call')
                self.name = self.find_qrz_value(callsign,'name')
                self.fname = self.find_qrz_value(callsign,'fname')
                self.addr1 = self.find_qrz_value(callsign,'addr1')
                self.addr2 = self.find_qrz_value(callsign,'addr2')
                self.state = self.find_qrz_value(callsign,'state')
                self.zip = self.find_qrz_value(callsign,'zip')
                self.country = self.find_qrz_value(callsign,'country')
                self.lat = self.find_qrz_value(callsign,'lat')
                self.lon = self.find_qrz_value(callsign,'lon')
                self.grid = self.find_qrz_value(callsign,'grid')
                self.county = self.find_qrz_value(callsign,'county')
                self.license_class = self.find_qrz_value(callsign,'class')
                self.qsl_direct = self.find_qrz_value(callsign,'mqsl')
                self.will_eqsl = self.find_qrz_value(callsign,'eqsl')
                self.qsl_lotw = self.find_qrz_value(callsign,'lotw')
        except Exception, e:
            self.error = unicode(e)
