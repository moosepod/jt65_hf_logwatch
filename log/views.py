from django.shortcuts import render_to_response
from django.template import RequestContext

from log.models import Entry

CALLSIGNS_PER_PAGE=5

def callsigns(request):
	seen_callsign = {}
	callsigns = []

	for e in Entry.objects.filter(callsign__isnull=False).order_by('-when'):
		if len(seen_callsign) == CALLSIGNS_PER_PAGE: 
			break
		if not seen_callsign.get(e.callsign):
			callsigns.append(
				{'callsign': e.callsign,
				 'name': 'Matt C',
				 'qth' : 'Niagara Falls, NY',
				 'distance': '54.3 miles'})
			seen_callsign[e.callsign] = True

	return render_to_response('callsigns.html',
                          {'callsigns': callsigns},
                          context_instance=RequestContext(request))

