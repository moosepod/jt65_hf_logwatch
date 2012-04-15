from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.safestring import mark_safe

from log.models import Entry,Contact
from qrz.models import QRZCredentials

def latest_callsigns_list(last_id):
	seen_callsign = {}
	callsigns = []
	
	qrz = QRZCredentials.objects.get(username=settings.CALLSIGN)

	# The order here attempts to match the JT65 log window ordering
	last_time = None
	# Using last ID here as a way to only get the latest entries isn't perfect
	# It assumes they will be sequentially allocated. That's good enough for 
	# what I'm trying to do here.
	for e in Entry.objects.filter(id__gte=last_id,
								  callsign__isnull=False).order_by('-when','-id'):
		if not last_time: last_time = e.when
		
		if last_time != e.when:
			break
		
		if not seen_callsign.get(e.callsign):
			q = qrz.lookup_callsign(e.callsign)
			r = {'qrz':      q, 
				 'id':       e.id,
				 'is_cq':    e.exchange.startswith('CQ'),
				 'contacts': list(Contact.objects.filter(callsign__iexact=e.callsign))}
			callsigns.append(r)
			seen_callsign[e.callsign] = True
			
	return callsigns
		
def callsigns(request):
	return render_to_response('log.html',
                          {'callsigns': latest_callsigns_list(0)},
                          context_instance=RequestContext(request))

def latest_callsigns_json(request):
	callsigns = latest_callsigns_list(int(request.GET.get('last_id','0')))
	if len(callsigns):
		html = mark_safe(render_to_string('callsigns.html', 
							{'callsigns': callsigns }))
		new_callsigns = True
		last_id = callsigns[-1]['id']
	else:
		html = ''
		new_callsigns = False
		last_id = 0
		
	json = simplejson.dumps({'html': html,
							 'last_id': last_id,
							 'has_new': new_callsigns})
	return HttpResponse(json,
						mimetype="application/json")


