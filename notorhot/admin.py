from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin

from notorhot.models import Competition, Candidate

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date_presented', 'date_voted', 'winner',)
    date_hierarchy = 'date_voted'
    search_fields = ('left__name', 'right__name',)
    raw_id_fields = ('left', 'right', 'winner',)
    

class CompetitionInline(admin.TabularInline):
    model = Competition
    

class LeftCompetitionInline(CompetitionInline):
    fk_name = 'left'
    extra = 0
    
    
class RightCompetitionInline(CompetitionInline):
    fk_name = 'right'
    extra = 0

class CandidateAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [LeftCompetitionInline, RightCompetitionInline,]
    
    list_display = ('__unicode__', 'pic', 'is_enabled', 'challenges', 'votes', 'wins',)
    date_hierarchy = 'added'
    search_fields = ('name',)
    list_filter = ('is_enabled', )
    

admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Candidate, CandidateAdmin)