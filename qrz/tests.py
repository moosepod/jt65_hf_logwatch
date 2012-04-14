from django.test import TestCase, Client
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from qrz.models import QRZRecord,QRZCredentials

BAD_SESSION = '<QRZDatabase xmlns="http://www.qrz.com" version="1.18"><Session><Error>Invalid session key</Error><GMTime>Sat Sep 3 21:15:09 2011</GMTime><Remark>cpu:	0.190s</Remark></Session></QRZDatabase>'
TIMEOUT_SESSION = '<QRZDatabase xmlns="http://www.qrz.com" version="1.18"><Session><Error>Session Timeout</Error><GMTime>Sat Sep 3 21:15:09 2011</GMTime><Remark>cpu:	0.190s</Remark></Session></QRZDatabase>'
GOOD_RECORD = '<?xml version="1.0" encoding="iso8859-1" ?> <QRZDatabase version="1.18" xmlns="http://www.qrz.com"> <Callsign> <call>KC2ZUF</call> <dxcc>291</dxcc> <name>A TEST RECORD</name> <fname>A Name</fname> <addr1>123 Fake St</addr1> <addr2>Fakeville</addr2> <state>NY</state> <zip>14043</zip> <country>United States</country> <lat>42.123456</lat> <lon>-78.987654</lon> <grid>FN02ld</grid> <county>Erie</county> <ccode>271</ccode> <fips>36029</fips> <land>United States</land> <efdate>2008-11-11</efdate> <expdate>2018-12-02</expdate> <trustee>KZ7AWP, FOO B QUUX</trustee> <class>C</class> <codes>HAB</codes> <email>fake@fake.com</email> <url>http://fake.fake.com</url> <u_qs>4923</u_qs> <bio>http://www.qrz.com/db/FAKEE</bio> <moddate>2011-02-18 17:31:07</moddate> <MSA>1280</MSA> <AreaCode>716</AreaCode> <eqsl>1</eqsl> <mqsl>1</mqsl> <TimeZone>Eastern</TimeZone> <GMTOffset>-5</GMTOffset> <DST>Y</DST> <cqzone>0</cqzone> <ituzone>0</ituzone> <locref>1</locref> <born>0000</born> <user>FA2KE</user> </Callsign> <Session> <Key>123456</Key> <Count>9</Count> <SubExp>Mon Sep 3 00:00:00 2012</SubExp> <GMTime>Sat Sep 3 20:03:52 2011</GMTime> <Remark>cpu:	0.077s </Remark> </Session> </QRZDatabase>'

class QRZCredentialsTest(TestCase):
    def test_url_failure(self):
        q = QRZCredentials(qrz_url='a',username='a',password='b')
        q.load_url = lambda x: None
        r = q.lookup_callsign('KC2ZUF')
        self.assertFalse(r.is_authenticated)
        self.assertEquals('Unable to log in to QRZ',r.error)

    def test_bad_session(self):
        q = QRZCredentials(qrz_url='a',username='a',password='b',session_id='abc')
        q.get_qrz_data = lambda x: BAD_SESSION
        r = q.lookup_callsign('KC2ZUF')
        self.assertFalse(r.is_authenticated)
        self.assertFalse(r.error)

    def test_good_lookup(self):
        q = QRZCredentials(qrz_url='a',username='a',password='b',session_id='abc')
        q.get_qrz_data = lambda x: GOOD_RECORD
        r = q.lookup_callsign('KC2ZUF')
        self.assertTrue(r.is_authenticated)
        self.assertFalse( r.error)
        self.assertEquals('KC2ZUF', r.call)

class QRZRecordTest(TestCase):
    def test_is_dx(self):
        qrz = QRZRecord()
        qrz.country = 'United States'
        self.assertFalse(qrz.is_dx())

        qrz.country = 'united states'
        self.assertFalse(qrz.is_dx())
    
        qrz.country = 'Canada'
        self.assertTrue(qrz.is_dx())

    def test_licence_class_expanded(self):
        qrz = QRZRecord()
        qrz.license_class = None
        self.assertEquals('Other', qrz.license_class_expanded())
        qrz.license_class = 'G'
        self.assertEquals('General', qrz.license_class_expanded())
        qrz.license_class = 'A'
        self.assertEquals('Advanced', qrz.license_class_expanded())
        qrz.license_class = 'N'
        self.assertEquals('Novice', qrz.license_class_expanded())
        qrz.license_class = 'T'
        self.assertEquals('Technician', qrz.license_class_expanded())
        qrz.license_class = 'E'
        self.assertEquals('Extra', qrz.license_class_expanded())

    def test_parse_error(self):
        qrz = QRZRecord(xml_data='asdfas')
        self.assertEquals(u'syntax error: line 1, column 0', qrz.error)

    def test_bad_session(self):
        qrz = QRZRecord(xml_data=BAD_SESSION)
        self.assertFalse(qrz.error)
        self.assertFalse(qrz.session_timeout)   
        self.assertFalse(qrz.is_authenticated)
    
    def test_timeout_session(self):
		qrz = QRZRecord(xml_data=TIMEOUT_SESSION)
		self.assertTrue(qrz.error)
		self.assertTrue(qrz.session_timeout)       
 		self.assertFalse(qrz.is_authenticated)
    
    def test_parse(self):
        qrz = QRZRecord(xml_data=GOOD_RECORD)

        self.assertFalse(qrz.session_timeout)   
        self.assertFalse(qrz.error)
        self.assertTrue(qrz.is_authenticated)
        self.assertEquals('A TEST RECORD',qrz.name)
        self.assertEquals('KC2ZUF',qrz.call)
        self.assertEquals('A Name',qrz.fname)
        self.assertEquals('123 Fake St',qrz.addr1)
        self.assertEquals('Fakeville',qrz.addr2)
        self.assertEquals('NY',qrz.state)
        self.assertEquals('14043',qrz.zip)
        self.assertEquals('Erie',qrz.county)
        self.assertEquals('42.123456',qrz.lat)
        self.assertEquals('-78.987654',qrz.lon)
        self.assertEquals('FN02ld',qrz.grid)
        self.assertEquals('United States',qrz.country)
        self.assertEquals('C',qrz.license_class)
        self.assertEquals('1',qrz.qsl_direct)
        self.assertEquals('1',qrz.will_eqsl)


