import datetime
from mock import Mock, patch

from django.test import TestCase
from django.forms import ValidationError
from django import forms

from notorhot._tests.factories import mixer
from notorhot.contrib.write_in.models import DefaultWriteIn
from notorhot.contrib.write_in.views import WriteInDefaultView, \
    WriteInThanksView

class URLConfMixin(object):
    urls = 'notorhot.contrib.write_in._tests.urls'


class WriteInDefaultViewTestCase(URLConfMixin, TestCase):
    def test_get_with_category(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        
        response = self.client.get('/write-in/cat-slug/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInDefaultView)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['form']._meta.model, DefaultWriteIn)
        self.assertTemplateUsed(response, 'write_in/defaultwritein_create.html')
        
    def test_get_non_public_category(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug', \
            is_public=False)
        
        response = self.client.get('/write-in/cat-slug/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInDefaultView)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['form']._meta.model, DefaultWriteIn)
        self.assertTemplateUsed(response, 'write_in/defaultwritein_create.html')
        
    def test_get_without_category(self):
        response = self.client.get('/write-in/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInDefaultView)
        self.assertIsNone(response.context['category'])
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['form']._meta.model, DefaultWriteIn)
        self.assertTemplateUsed(response, 'write_in/defaultwritein_create.html')
        
    def test_get_invalid_category(self):
        # We should probably 404, but I'm still trying to figure out how to 
        # do that without having to catch an exception in every CategoryMixin
        # subclass, and this is not ideal behavior, but neither is it
        # pathological.
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug', \
            is_public=False)
        
        response = self.client.get('/write-in/wrong-slug/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInDefaultView)
        self.assertIsNone(response.context['category'])
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['form']._meta.model, DefaultWriteIn)
        self.assertTemplateUsed(response, 'write_in/defaultwritein_create.html')
        
    def test_invalid_form(self):
        with patch.object(forms.ModelForm, 'is_valid') as mock_is_valid:
            mock_is_valid.return_value = False
    
            response = self.client.post('/write-in/', data={})
            
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.context['view'], WriteInDefaultView)
            self.assertIsNone(response.context['category'])
            self.assertIsNotNone(response.context['form'])
            self.assertEqual(response.context['form']._meta.model, DefaultWriteIn)
            self.assertTemplateUsed(response, 'write_in/defaultwritein_create.html')
        
    def test_success(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug', id=1)
        
        self.assertEqual(DefaultWriteIn.objects.count(), 0)
        
        with patch.object(forms.ModelForm, 'is_valid') as mock_is_valid:
            mock_is_valid.return_value = True
    
            response = self.client.post('/write-in/', data={
                    'candidate_name': 'candidate',
                    'submitter_name': 'submitter',
                    'submitter_email': 'submitter@example.com',
                    'category': 1,
                })
            
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/write-in/cat-slug/thanks/')
            self.assertEqual(DefaultWriteIn.objects.count(), 1)
            self.assertEqual(cat1.defaultwritein_write_ins.count(), 1)

class WriteInThanksViewTestCase(URLConfMixin, TestCase):
    def test_success(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug')
        
        response = self.client.get('/write-in/cat-slug/thanks/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInThanksView)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertTemplateUsed(response, 'write_in/thanks.html')
        
    def test_invalid_category(self):        
        response = self.client.get('/write-in/cat-slug/thanks/')        
        self.assertEqual(response.status_code, 404)
        
    def test_non_public_category(self):
        cat1 = mixer.blend('notorhot.CandidateCategory', slug='cat-slug', 
            is_public=False)
        
        response = self.client.get('/write-in/cat-slug/thanks/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['view'], WriteInThanksView)
        self.assertIsNotNone(response.context['category'])
        self.assertEqual(response.context['category'], cat1)
        self.assertTemplateUsed(response, 'write_in/thanks.html')