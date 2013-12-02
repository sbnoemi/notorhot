import datetime
from mock import Mock, patch, MagicMock, PropertyMock

from django.test import TestCase
from django import forms
from django.http import Http404

from notorhot._tests.factories import mixer
from notorhot._tests._utils import setup_view, ViewTestMixin
from notorhot.contrib.write_in._tests.models import SimpleWriteIn
from notorhot.contrib.write_in.models import DefaultWriteIn
from notorhot.contrib.write_in.views import WriteInBaseView, WriteInDefaultView, \
    WriteInThanksView
    

class WriteInBaseViewTestCase(ViewTestMixin, TestCase):
    view_class = WriteInBaseView
    
    def test_assign_fields(self):
        # make sure that changing fields / exclude_fields on a view instance
        # doesn't change the attribute on the class
        view = self.make_view('get')
        view.fields = ['field1',]
        view.exclude_fields = ['field2',]
        
        self.assertNotEqual(self.view_class.fields, ['field1',])
        self.assertNotEqual(self.view_class.exclude_fields, ['field2',])
    
    def test_get_category(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get', request_kwargs={ 'category_slug': cat.slug, })
        
        view_cat = view.get_category()
        self.assertEqual(view_cat, cat)
        
        cat = mixer.blend('notorhot.CandidateCategory', is_public=False)
        view = self.make_view('get', request_kwargs={ 'category_slug': cat.slug, })
        
        view_cat = view.get_category()
        self.assertIsNotNone(view_cat)
        
        # should be able to run with or without category
        view = self.make_view('get')
        view_cat = view.get_category()
        
    def test_get_form_class_with_category(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get', request_kwargs={ 'category_slug': cat.slug, })

        form_class = view.get_form_class()
        self.assertItemsEqual(form_class.base_fields.keys(), 
            ['candidate_name', 'submitter_name', 'submitter_email'])

        # make sure we remove the category from fields / add to exclude
        view = self.make_view('get', request_kwargs={ 'category_slug': cat.slug, })
        view.fields = ['category', 'candidate_name',]
        self.assertIn('category', view.fields)   
        self.assertNotIn('category', view.exclude_fields)     
        
        form_class = view.get_form_class()
        self.assertNotIn('category', view.fields)
        self.assertIn('category', view.exclude_fields)
        
    def test_get_form_class_without_category(self):
        cat = mixer.blend('notorhot.CandidateCategory')
        view = self.make_view('get')

        form_class = view.get_form_class()
        self.assertItemsEqual(form_class.base_fields.keys(), 
            ['candidate_name', 'submitter_name', 'submitter_email', 'category'])

        # make sure we add the category to fields / remove from exclude
        view = self.make_view('get')
        view.fields = ['candidate_name',]
        view.exclude_fields.append('category')
        self.assertNotIn('category', view.fields)   
        self.assertIn('category', view.exclude_fields)     
        
        form_class = view.get_form_class()
        self.assertIn('category', view.fields)
        self.assertNotIn('category', view.exclude_fields)
        
        # but don't add to fields if no fields set
        view = self.make_view('get')
        self.assertItemsEqual(view.fields, []) 
        
        form_class = view.get_form_class()
        self.assertItemsEqual(view.fields, [])
    

class WriteInDefaultViewTestCase(ViewTestMixin, TestCase):
    view_class = WriteInDefaultView
    
    def test_init(self):
        view = self.make_view('get')
        self.assertEqual(view.fields, view.default_fields)
        self.assertEqual(view.exclude_fields, 
            ['date_submitted', 'date_processed', 'status',])


class WriteInThanksViewTestCase(ViewTestMixin, TestCase):
    view_class = WriteInThanksView
    
    def test_get_category(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='cat1')        
        view = self.make_view('get', request_kwargs={ 'category_slug': 'cat1', })

        try:
            view_cat = view.category
        except Http404:
            self.fail(u"WriteInThanksView should be able to retrieve existing "
                "category.")
        else:
            self.assertEqual(cat, view_cat)
            
        view = self.make_view('get', request_kwargs={ 'category_slug': 'cat2', })
        with self.assertRaises(Http404):
            view_cat = view.category