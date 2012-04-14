from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from log.models import Entry,Contact
from qrz.models import QRZCredentials

CALLSIGNS_PER_PAGE=10

def callsigns(request):
	seen_callsign = {}
	callsigns = []

	qrz = QRZCredentials.objects.get(username=settings.CALLSIGN)

	# The order here attempts to match the JT65 log window ordering
	last_time = None
	for e in Entry.objects.filter(callsign__isnull=False).order_by('-when','-id'):
		if not last_time: last_time = e.when
		if last_time != e.when:
			new_row = True
			last_time = e.when
		else:
			new_row = False
			
		if len(seen_callsign) == CALLSIGNS_PER_PAGE: 
			break
		if not seen_callsign.get(e.callsign):
			q = qrz.lookup_callsign(e.callsign)
			r = {'qrz':      q, 
				 'new_row':  new_row,
				 'is_cq':    e.exchange.startswith('CQ'),
				 'contacts': list(Contact.objects.filter(callsign__iexact=e.callsign))}
			callsigns.append(r)
			seen_callsign[e.callsign] = True

	return render_to_response('callsigns.html',
                          {'callsigns': callsigns},
                          context_instance=RequestContext(request))

