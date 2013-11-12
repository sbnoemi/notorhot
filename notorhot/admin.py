from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin

from notorhot.models import Competition, Candidate, CandidateCategory


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'category', 'date_presented', 'date_voted', 
        'winner',)
    date_hierarchy = 'date_voted'
    list_filter = ('category',)
    search_fields = ('left__name', 'right__name',)
    raw_id_fields = ('left', 'right', 'winner', 'category',)
    

class CompetitionInline(admin.TabularInline):
    model = Competition
    

class LeftCompetitionInline(CompetitionInline):
    fk_name = 'left'
    extra = 0
    
    
class RightCompetitionInline(CompetitionInline):
    fk_name = 'right'
    extra = 0

class CandidateAdmin(AdminImageMixin, admin.ModelAdmin):    
    list_display = ('__unicode__', 'pic', 'category', 'is_enabled', 
        'challenges', 'votes', 'wins',)
    date_hierarchy = 'added'
    search_fields = ('name',)
    list_filter = ('is_enabled', 'category',)
    raw_id_fields = ('category',)
    

class CandidateInline(AdminImageMixin, admin.StackedInline):
    model = Candidate
    inline_classes = ('grp-collapse grp-open',)


class CategoryAdmin(admin.ModelAdmin):
    inlines = [CandidateInline,]
    list_display = ('__unicode__', 'is_public', 'num_voted_competitions')
    list_filter = ('is_public',)
    search_fields = ('name',)


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(CandidateCategory, CategoryAdmin)