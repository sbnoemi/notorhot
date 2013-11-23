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
        'localized_fields', 'labels', 'help_texts', 'error_messages',]

    def get_form_class(self):
        """
        Returns the form class to use in this view.  

        Field selection logic matches that of standard CreateView, except that:

        * if :attr:`fields` attribute is empty, it will create the ModelForm 
        using a list of all fields on the model, excluding any specified in the 
        :attr:`exclude_fields` attribute. **NOTE**: This will sort fields 
        alphabetically.  To specify field order, use the :attr:`fields` class
        attribute instead.

        * any view class or instance attributes matching keyword args to 
        :func:`modelform_factory()` will be passed into the factory, permitting the 
        developer to set labels, help_text, etc. simply by subclassing the view and 
        setting the appropriate class attributes.  The exception is the 
        :attr:`exclude` keyword argument; but the :attr:`exclude_fields` attribute
        has the same effect.
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
            
        if self.fields is None:
            # _meta.get_all_field_names() gives us the fields for the form
            # but in the wrong order.
            fields_for_form = model._meta.get_all_field_names()
            
            # but _meta.fields is in the correct order
            fields = [f.name for f in model._meta.fields if f.name in fields_for_form]
            
            if self.exclude_fields:
                # we could do this with set conversions, but it screws up field
                # order.
                fields = [f for f in fields if f not in self.exclude_fields]
        else:
            fields = copy(self.fields)

        kwargs = {}
        for kwarg_name in self.MODELFORM_KWARGS:
            val = getattr(self, kwarg_name, None)
            if val:
                kwargs[kwarg_name] = val

        return modelform_factory(model, fields=fields, **kwargs)


class AbstractFieldTracker(FieldTracker):
    def finalize_class(self, sender, name, **kwargs):
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super(AbstractFieldTracker, self).finalize_class(sender, **kwargs)

    
