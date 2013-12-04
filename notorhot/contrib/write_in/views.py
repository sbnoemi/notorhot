from copy import copy

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _, ugettext_lazy as _l
from django.core.urlresolvers import reverse
from django.views.generic.base import View, TemplateView
from django.utils.safestring import mark_safe
from django.conf import settings

from notorhot.utils import CategoryMixin
from notorhot.contrib.write_in.utils import get_write_in_model, \
    get_write_in_model_name, RichFormFactoryCreateView


# Create your views here.
class WriteInBaseView(CategoryMixin, RichFormFactoryCreateView):
    """
    A :class:`~django.views.edit.CreateView` subclass that can be used to record
    write-in candidates to be stored in any model that inherits from 
    :class:`~notorhot.contrib.write_in.WriteInBase`.  Works "out of the box" or
    can be subclassed to hide fields for custom model classes, change the success
    URL, or implement additional functionality.
    
    Inherits from 
    :class:`~notorhot.contrib.write_in.utils.RichFormFactoryCreateView` to allow
    for further ModelForm customization by setting additional class attributes
    on the view.  Subclass this view and set class attributes to achieve 
    custom form display or other custom view behavior.
    
    If used with a URL that passes a ``category_slug`` keyword, this view will
    hide the "category" field from the form displayed and automatically assign
    write-ins to the appropriate category based on the category slug in the URL.
    
    If used with a URL that omits the ``category_slug`` keyword, this view will
    give the user a choice of all categories in the database to assign their 
    write-in candidate to.
    
    This view permits assigning write-ins to non-public categories.
    """

    allowed_methods = ['get', 'post',]
    model = get_write_in_model()
    template_name_suffix = '_create'
    exclude_fields = ['date_submitted', 'date_processed', 'status',]
    fields = []
    
    def __init__(self, *args, **kwargs):
        # if we don't copy this, then changes made in one instance apply to the 
        # class and all instances, since fields and exclude_fields are 
        # references rather than primitives.
        self.fields = copy(self.fields)
        self.exclude_fields = copy(self.exclude_fields)
        super(WriteInBaseView, self).__init__(*args, **kwargs)
        
            
    def get_category(self):
        return self._get_category()
    
    # TODO: refactor
    def get_form_class(self):
        """
        Override ensures that "category" field is included or excluded from 
        write-in form depending on whether a category was passed in the URL.
        """
        if self.category is None:
            # if we don't have a category, let the user choose it.
            if 'category' in self.exclude_fields:
                self.exclude_fields.remove('category')
            
            # if we haven't listed fields out, we'll use all fields, so 
            # don't add to an empty list
            if self.fields and 'category' not in self.fields:
                if 'candidate_name' in self.fields:
                    insert_index = self.fields.index('candidate_name') + 1
                    self.fields.insert(insert_index, 'category')
                else:
                    self.fields.append('category')

        else:
            # if we have a category, don't show it in the form
            if 'category' not in self.exclude_fields:
                self.exclude_fields.append('category')
            if 'category' in self.fields:
                self.fields.remove('category')
        
        return super(WriteInBaseView, self).get_form_class()
        
    def get_success_url(self):
        category = self.object.category
        return reverse('write_in_thanks', kwargs={ 'category_slug': category.slug })
        
        
class WriteInDefaultView(WriteInBaseView):
    """
    :class:`WriteInBaseView` subclass customized for use with 
    :class:`~notorhot.contrib.write_in.models.DefaultWriteIn` as the write-in
    storage model.
    
    Can also be used with any other write-in model that subclasses both
    :class:`~notorhot.contrib.write_in.models.DefaultWriteIn` and 
    :class:`~notorhot.contrib.write_in.models.SubmitterInfoMixin`
    """
    default_fields = [
            'submitter_name', 'submitter_email', 'candidate_name', 'category',
        ]
    labels = {
            'submitter_name': _l(u"Your Name"),
            'submitter_email': _l(u"Your Email"),
        }
    
    def __init__(self, *args, **kwargs):
        super(WriteInDefaultView, self).__init__(*args, **kwargs)
        
        # If we're using the default model, we can specify our fields explicitly
        # if they haven't been explicitly overridden
        if getattr(self, 'fields', []) == [] and \
                get_write_in_model_name() == 'write_in.DefaultWriteIn':
            self.fields = self.default_fields
        
        
class WriteInThanksView(CategoryMixin, TemplateView):
    """
    Displays a "success" page after a write-in is submitted.
    """
    template_name = 'write_in/thanks.html'
    allowed_methods = ['get',]
    
    def get_category(self):
        category = self._get_category()
        if not category:
            raise Http404
        return category
        
