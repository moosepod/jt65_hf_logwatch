from django.contrib import admin

from log.models import Entry,JT65LogFile

class EntryAdmin(admin.ModelAdmin):
	model = Entry

	list_display=('when','frequency','db','exchange','callsign')

admin.site.register(Entry,EntryAdmin)

class JT65LogFileAdmin(admin.ModelAdmin):
	model = JT65LogFile

admin.site.register(JT65LogFile,JT65LogFileAdmin)
