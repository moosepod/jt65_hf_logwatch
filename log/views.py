from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.safestring import mark_safe

from log.models import Entry,Contact
from qrz.models import QRZCredentials

def latest_callsigns_list():
	seen_callsign = {}
	callsigns = []
	
	qrz = QRZCredentials.objects.get(username=settings.CALLSIGN)

	# The order here attempts to match the JT65 log window ordering
	last_time = None
	for e in Entry.objects.filter(callsign__isnull=False).order_by('-when','-id'):
		if not last_time: last_time = e.when
		
		if last_time != e.when:
			break
		
		if not seen_callsign.get(e.callsign):
			q = qrz.lookup_callsign(e.callsign)
			r = {'qrz':      q, 
				 'is_cq':    e.exchange.startswith('CQ'),
				 'contacts': list(Contact.objects.filter(callsign__iexact=e.callsign))}
			callsigns.append(r)
			seen_callsign[e.callsign] = True
			
	return callsigns
		
def callsigns(request):
	return render_to_response('log.html',
                          {'callsigns': latest_callsigns_list()},
                          context_instance=RequestContext(request))

def latest_callsigns_json(request):
	callsigns = latest_callsigns_list()
	if len(callsigns):
		html = mark_safe(render_to_string('callsigns.html', 
							{'callsigns': callsigns }))
		new_callsigns = True
	else:
		html = ''
		new_callsigns = False
	json = simplejson.dumps({'html': html,'has_new': new_callsigns})
	return HttpResponse(json,
						mimetype="application/json")


