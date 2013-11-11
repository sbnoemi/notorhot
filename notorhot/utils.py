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