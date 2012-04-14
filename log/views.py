from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from log.models import Entry
from qrz.models import QRZCredentials

CALLSIGNS_PER_PAGE=5

def callsigns(request):
	seen_callsign = {}
	callsigns = []

	qrz = QRZCredentials.objects.get(username=settings.CALLSIGN)

	for e in Entry.objects.filter(callsign__isnull=False).order_by('-when','id'):
		if len(seen_callsign) == CALLSIGNS_PER_PAGE: 
			break
		if not seen_callsign.get(e.callsign):
			r = qrz.lookup_callsign(e.callsign)
			callsigns.append(r)
			seen_callsign[e.callsign] = True

	return render_to_response('callsigns.html',
                          {'callsigns': callsigns},
                          context_instance=RequestContext(request))

