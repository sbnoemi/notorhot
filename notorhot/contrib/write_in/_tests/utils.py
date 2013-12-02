import datetime
from mock import patch, Mock

from django import forms
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.test import TestCase

from notorhot._tests._utils import setup_view, ViewTestMixin
from notorhot._tests.factories import mixer
from notorhot.models import CandidateCategory
from notorhot.contrib.write_in.models import DefaultWriteIn
from notorhot.contrib.write_in.utils import get_write_in_model_name, \
    get_write_in_model, RichFormFactoryCreateView, AbstractFieldTracker
from notorhot.contrib.write_in._tests._utils import ModelTestCase
from notorhot.contrib.write_in._tests.models import SimpleWriteIn

from model_utils.tracker import FieldTracker, FieldInstanceTracker


class ModelSelectionTestCase(ModelTestCase):
    apps = ('notorhot.contrib.write_in._tests',)    
    
    def test_defaults(self):
        with self.settings(NOTORHOT_SETTINGS={}):
            self.assertEqual(get_write_in_model_name(), 'write_in.DefaultWriteIn')
            self.assertEqual(get_write_in_model(), DefaultWriteIn)
        
    def test_custom(self):
        with self.settings(NOTORHOT_SETTINGS={ 
                    'WRITE_IN_MODEL': '_tests.SimpleWriteIn' 
                }):
            self.assertEqual(get_write_in_model_name(), '_tests.SimpleWriteIn')
            self.assertEqual(get_write_in_model(), SimpleWriteIn)
    

class AbstractFieldTrackerTestCase(TestCase):
    def test_finalize_class(self):
        tracker = AbstractFieldTracker(fields=['whatever',])
        with patch.object(FieldTracker, 'finalize_class') as mock_finalize:
            tracker.finalize_class('a_sender', 'a_name')
            self.assertEqual(mock_finalize.call_count, 1)
            self.assertEqual(mock_finalize.call_args[0], ('a_sender',))
            self.assertEqual(tracker.name, 'a_name')
            self.assertEqual(tracker.attname, '_a_name')


class RFFCVTextMixin(object):
    class Model(models.Model):
        # fields declared in reverse order to test alphabetical vs declared sorting
        field3 = models.IntegerField()
        field2 = models.IntegerField()
        field1 = models.IntegerField()

    def get_form_class(self, view_class):
        self.view_class = view_class
        view = self.make_view('get')
        return view.get_form_class()

    
class RFFCVModelTestCase(RFFCVTextMixin, ViewTestMixin, TestCase):
    def test_with_declared_form_class(self):        
        class View(RichFormFactoryCreateView):
            form_class = 'whatever'
        
        form_class = self.get_form_class(View)
        self.assertEqual(form_class, 'whatever')
        
    def test_with_declared_model(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            
        form_class = self.get_form_class(View)
        self.assertEqual(form_class._meta.model, self.Model)
        
        
    def test_with_object(self):
        instance = mixer.blend(self.Model)

        class View(RichFormFactoryCreateView):
            object = instance

        form_class = self.get_form_class(View)
        self.assertEqual(form_class._meta.model, self.Model)
        
    def test_with_queryset(self):
        class View(RichFormFactoryCreateView):
            queryset = self.Model.objects.all()

        form_class = self.get_form_class(View)
        self.assertEqual(form_class._meta.model, self.Model)


class RFFCVFieldsTestCase(RFFCVTextMixin, ViewTestMixin, TestCase):
    def test_with_no_declared_fields(self):
        class View(RichFormFactoryCreateView):
            model = self.Model

        form_class = self.get_form_class(View)
        self.assertEqual(form_class.base_fields.keys(), ['field3', 'field2', 'field1',])
        
    def test_with_empty_declared_fields(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            fields = []

        form_class = self.get_form_class(View)
        self.assertEqual(form_class.base_fields.keys(), ['field3', 'field2', 'field1',])
    
    def test_with_declared_fields(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            fields = ['field1', 'field2',]

        form_class = self.get_form_class(View)
        self.assertEqual(form_class.base_fields.keys(), ['field1', 'field2',])
        
    def test_with_only_excluded_fields(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            exclude_fields = ['field3',]

        form_class = self.get_form_class(View)
        self.assertEqual(form_class.base_fields.keys(), ['field2', 'field1',])
        
    def test_with_declared_and_excluded_fields(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            fields = ['field1', 'field2',]
            exclude_fields = ['field2',]

        form_class = self.get_form_class(View)
        self.assertEqual(form_class.base_fields.keys(), ['field1',])
        
    def test_modelform_kwargs(self):
        class View(RichFormFactoryCreateView):
            model = self.Model
            form = 'form_class'
            formfield_callback = 'callback_function'
            widgets = 'widget_dict'
            localized_fields = 'field_list'
            labels = 'label_dict'
            help_texts = 'help_text_dict'
            error_messages = 'error_message_dict'            
            
        from notorhot.contrib.write_in import utils as write_in_utils
        with patch.object(write_in_utils, 'modelform_factory') as mock_factory:
            form_class = self.get_form_class(View)
            self.assertEqual(mock_factory.call_count, 1)
            self.assertEqual(mock_factory.call_args[0], (self.Model,))
            self.assertEqual(mock_factory.call_args[1], {
                    'form': 'form_class',
                    'formfield_callback': 'callback_function',
                    'widgets': 'widget_dict',
                    'localized_fields': 'field_list',
                    'labels': 'label_dict',
                    'help_texts': 'help_text_dict',
                    'error_messages': 'error_message_dict',
                })
