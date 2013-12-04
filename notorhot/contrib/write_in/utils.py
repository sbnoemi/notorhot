from copy import copy

from django.conf import settings
from django.views.generic.edit import CreateView
from django.db.models import get_model
from django.forms.models import modelform_factory

from model_utils import FieldTracker

def get_write_in_model_name():
    """
    Retrieves the name of the model (in form "appname.ModelName") defined in 
    ``settings.NOTORHOT_SETTINGS['WRITE_IN_MODEL']``, to be used to store 
    write-in submissions.  
    
    If the setting has not been defined, defaults to 
    ``"write_in.DefaultWriteIn"``.  
    
    This allows for developers to specify an alternative model for write-in 
    storage.
    
    :returns: write-in storage model name in form "appname.ModelName"
    :rtype: string
    """
    notorhot_settings = getattr(settings, 'NOTORHOT_SETTINGS', {})
    return notorhot_settings.get('WRITE_IN_MODEL', 'write_in.DefaultWriteIn')

def get_write_in_model():
    """
    Retrieves the model class (specified in 
    ``settings.NOTORHOT_SETTINGS['WRITE_IN_MODEL']``) to be used to store 
    write-in submissions.  See :func:`get_write_in_model_name` for details
    
    :returns: write-in storage model class (**not** an instance)
    :rtype: :class:`django.db.models.Model` 
    """
    model_name = get_write_in_model_name()
    return get_model(*model_name.split('.'))
    

class RichFormFactoryCreateView(CreateView):
    """
    Subclass of :class:`~django.views.generic.edit.CreateView` that allows
    the developer to specify more arguments to 
    :func:`~django.forms.models.modelform_factory` in order to further
    customize the form generated.
    """
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
        `Django documentation <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#modelforms-factory>`_.
        
        :returns: form class (**not** an instance) to use for view
        :rtype: :class:`django.forms.models.ModelForm`
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
                    
        # There's no case I can think of where you'd want to build a form with 
        # NO fields, but in some cases we use an empty list so we don't have to 
        # check before iterating.
        # So we'll interpret an empty list or tuple as meaning that we should 
        # use the default fields for the model.
        # If you really want *no* fields, subclass and override this method.
        if kwargs.get('fields') in ([], ()):
            kwargs['fields'] = None

        return modelform_factory(model, **kwargs)


class AbstractFieldTracker(FieldTracker):
    """
    Subclass of django-model-utils :class:`model_utils.FieldTracker` that can be
    added to abstract models and will apply properly to concrete children of
    those models.
    
    This FieldTracker must be applied in the abstract model's ``.__init__()``
    method, as a workaround to a shortcoming of Django's model inheritance. 
    
    See
    `this pull request <https://github.com/carljm/django-model-utils/pull/80>`_
    for details on the model inheritance problem.
    
    See source of :class:`~notorhot.contrib.write_in.models.WriteInBase` for a 
    usage example.
    """
    
    def finalize_class(self, sender, name, **kwargs):
        """
        Should be called from the ``.__init__()`` method of the abstract model
        to which this tracker is added. 
        
        Sets some instance variables that for a non-abstract model would have
        been set during ``.contribute_to_class()``, then calls parent method to
        properly add tracker to the ``sender`` class.
        
        :param sender: Class to which the tracker should be attached
        :type sender: :class:`django.db.models.Model`
        :param string name: the attribute name that should be used for the
            tracker on the class that it is being attached to.  For instance, if
            you call ``some_tracker.finalize_class(MyModel, 'myattr')``, then
            later ``MyModel.myattr`` will return ``some_tracker``.
        """
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super(AbstractFieldTracker, self).finalize_class(sender, **kwargs)
