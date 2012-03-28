from django.contrib import admin

from log.models import Entry

class EntryAdmin(admin.ModelAdmin):
	model = Entry

	list_display=('when','frequency','db','exchange')

admin.site.register(Entry,EntryAdmin)
