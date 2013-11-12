from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# borrowed from https://github.com/brack3t/django-braces/pull/46
# This stuff really should be in Django core.
class NeverCacheMixin(object):
    """
    Mixin that makes sure View is never cached.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)
        
        
class ExecutableQuerysetMixin(object):
    def get_object(self, queryset=None):
        # Basically, we want to be able to specify a queryset to be 
        # executed at runtime instead of loadtime, using a custom 
        # manager instead of just defining the object we operate on.
        
        if queryset is None:
            qse = getattr(self, 'queryset_executable', None)
            if qse:
                return super(ExecutableQuerysetMixin, self).get_object(
                    queryset=qse())
            else:
                return super(ExecutableQuerysetMixin, self).get_object()
        else:
            return super(ExecutableQuerysetMixin, self).get_object(
                queryset=queryset)