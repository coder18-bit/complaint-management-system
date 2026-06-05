from django.contrib import admin
from .models import Complaint, Engineer, ComplaintHistory

admin.site.register(Engineer)
admin.site.register(Complaint)
admin.site.register(ComplaintHistory)