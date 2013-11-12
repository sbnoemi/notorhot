from django.utils.decorators import method_decorator
from django.utils.functional import lazy_property
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin

from notorhot.models import CandidateCategory

# borrowed from https://github.com/brack3t/django-braces/pull/46
# This stuff really should be in Django core.
class NeverCacheMixin(object):
    """
    Mixin that makes sure View is never cached.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)
        
        
class WorkingSingleObjectMixin(SingleObjectMixin):   
    def dispatch(self, *args, **kwargs):
        # SingleObjectMixin requires but doesn't provide this.  WTF?
        self.object = self.get_object()
        return super(WorkingSingleObjectMixin, self).dispatch(*args, **kwargs)
    

class CategoryMixin(object):
    def _get_category(self, slug_name='category_slug'):
        cat = None
        
        cat_slug = self.kwargs.get(slug_name)
        if cat_slug:
            try:
                cat = CandidateCategory.objects.get(slug=cat_slug)
            except CandidateCategory.DoesNotExist:
                pass
        
        return cat
    
    def get_category(self):
        raise NotImplementedError
        
    category = lazy_property(get_category)

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryMixin, self).get_context_data(*args, **kwargs)
                
        context.update({ 'category': self.category, })
        
        return context