from django.contrib import admin
from django.conf import settings

# Register your models here.
from notorhot.contrib.write_in.models import DefaultWriteIn
from notorhot.contrib.write_in.utils import get_write_in_model_name, \
    get_write_in_model

def use_default_admin():
    notorhot_settings = getattr(settings, 'NOTORHOT_SETTINGS', {})
    return notorhot_settings.get('USE_DEFAULT_ADMIN', True)

class DefaultWriteInAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'category', 'status', 'date_submitted', 
        'date_processed',]
    list_filter = ['category', 'status',]
    search_fields = ['candidate_name', 'submitter_name', 'submitter_email',]
    date_hierarchy = 'date_submitted'
    readonly_fields = ['date_submitted',]

if use_default_admin():
    admin.site.register(get_write_in_model(), DefaultWriteInAdmin)