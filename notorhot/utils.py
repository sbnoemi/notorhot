from django.utils.decorators import method_decorator
from django.utils.functional import lazy_property
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin

from notorhot.models import CandidateCategory

# borrowed from https://github.com/brack3t/django-braces/pull/46
# This stuff really should be in Django core.
class NeverCacheMixin(object):
    """
    Mixin that makes sure the :class:`~django.views.generic.base.View` it's 
    mixed into is never cached.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)
        
        
class WorkingSingleObjectMixin(SingleObjectMixin):  
    """
    Django's :class:`~django.views.generic.detail.SingleObjectMixin` requires 
    :attr:`object` attribute to be set (as is done in :meth:`.dispatch()` in 
    most of the views it's mixed into) but doesn't actually do the setting 
    itself -- making the mixin fairly useless on its own.
    
    This subclass simply sets :attr:`object` in :meth:`.dispatch()`.
    """
    def dispatch(self, *args, **kwargs):
        # SingleObjectMixin requires but doesn't provide this.  WTF?
        self.object = self.get_object()
        return super(WorkingSingleObjectMixin, self).dispatch(*args, **kwargs)
    

class CategoryMixin(object):
    """
    View mixin that adds a lazily-evaluated :attr:`category` property to 
    the view that references a :class:`~notorhot.models.CandidateCategory` 
    instance, and adds that instance to the context as ``category``.  
    
    A method is provided to determine the category from the ``category_slug``
    keyword argument to the view, but each class that uses the mixin must
    override :meth:`.get_category()` to indicate how the category should be
    determined -- e.g. from an attribute of the primary object the view operates
    on.
    """
    def _get_category(self, slug_name='category_slug'):
        """
        Retrieves a :class:`~notorhot.models.CandidateCategory` instance based 
        on the view keyword argument with the name indicated in the 
        ``slug_name`` parameter to this method.
        
        :param string slug_name: name of the view keyword argument containing 
            the category slug
        """
        cat = None
        
        cat_slug = self.kwargs.get(slug_name)
        if cat_slug:
            try:
                cat = CandidateCategory.objects.get(slug=cat_slug)
            except CandidateCategory.DoesNotExist:
                pass
        
        return cat
    
    def get_category(self):
        """
        Method that sets :attr:`category` attribute on the view.  Raises 
        :exc:`NotImplementedError` and thus must be overridden by any class 
        that uses this mixin.
        """
        raise NotImplementedError
        
    category = lazy_property(get_category)

    def get_context_data(self, *args, **kwargs):
        """
        Appends :attr:`category` attribute to context as ``category`` context 
        variable.
        """
    
        context = super(CategoryMixin, self).get_context_data(*args, **kwargs)
                
        context.update({ 'category': self.category, })
        
        return context