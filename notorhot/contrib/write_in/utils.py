from copy import copy

from django.conf import settings
from django.views.generic.edit import CreateView
from django.db.models import get_model
from django.forms.models import modelform_factory

from model_utils import FieldTracker

def get_write_in_model_name():
    notorhot_settings = getattr(settings, 'NOTORHOT_SETTINGS', {})
    return notorhot_settings.get('WRITE_IN_MODEL', 'write_in.DefaultWriteIn')

def get_write_in_model():
    model_name = get_write_in_model_name()
    return get_model(*model_name.split('.'))
    

class RichFormFactoryCreateView(CreateView):
    MODELFORM_KWARGS = ['form', 'formfield_callback', 'widgets', 
        'localized_fields', 'labels', 'help_texts', 'error_messages',
        'fields', 'exclude_fields']

    # @TODO: refactor custom logic into separate method for ease of testing.
    def get_form_class(self):
        """
        Returns the form class to use in this view.  

        Field selection logic matches that of standard CreateView, except that 
        any view class or instance attributes matching keyword args to 
        :func:`modelform_factory()` will be passed into the factory, permitting the 
        developer to set labels, help_text, etc. simply by subclassing the view and 
        setting the appropriate class attributes.  The exception is the 
        :attr:`exclude` keyword argument; but the :attr:`exclude_fields` attribute
        has the same effect.
        
        For a list of available keys and their types, see the 
        `Django documentation <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#modelforms-factory`_.
        """
        if self.form_class:
            return self.form_class

        if self.model is not None:
            # If a model has been explicitly provided, use it
            model = self.model
        elif hasattr(self, 'object') and self.object is not None:
            # If this view is operating on a single object, use
            # the class of that object
            model = self.object.__class__
        else:
            # Try to get a queryset and extract the model class
            # from that
            model = self.get_queryset().model
            
        if not hasattr(self, 'fields') and not hasattr(self, 'exclude_fields'):
            raise ValueError(u"Must set either fields or exclude_fields on "
                u"RichFormFactoryCreateView subclass")
            
        kwargs = {}
        for kwarg_name in self.MODELFORM_KWARGS:
            val = getattr(self, kwarg_name, None)
            if val is not None:
                # really, we should just rename the attribute to "exclude", but
                # a) that name is abiguous, and b) I'm feeling lazy about
                # updating the rest of the codebase.  May do later.
                if kwarg_name == 'exclude_fields':
                    kwargs['exclude'] = val
                else:
                    kwargs[kwarg_name] = val

        return modelform_factory(model, **kwargs)


class AbstractFieldTracker(FieldTracker):
    def finalize_class(self, sender, name, **kwargs):
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super(AbstractFieldTracker, self).finalize_class(sender, **kwargs)

    
