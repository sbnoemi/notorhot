import datetime
from mock import Mock, patch

from django.test import TestCase
from django.views.generic.base import View, TemplateView
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from notorhot._tests.factories import mixer
from notorhot._tests._utils import setup_view, ViewTestMixin
from notorhot.models import CandidateCategory, Candidate, Competition
from notorhot.utils import NeverCacheMixin, WorkingSingleObjectMixin, \
    CategoryMixin, ResetContentTemplateResponse

@never_cache
def never_cache_procedural(unused_arg):
    return HttpResponse('hi')

class NeverCacheView(NeverCacheMixin, View):
    def get(self, request):
        return HttpResponse('hi')


class WorkingSingleObjectView(WorkingSingleObjectMixin, View):
    def get(self, request):
        return HttpResponse('hi')
    

class CategoryView(CategoryMixin, View):
    def get(self, request):
        return HttpResponse('hi')
        

class ImplementedCategoryView(CategoryMixin, TemplateView):
    def get_category(self):
        return 'a category'
        

class ResetContentResponseTestCase(TestCase):
    def test_status_code(self):
        resp = ResetContentTemplateResponse('hi')
        self.assertEqual(resp.status_code, 205)


class NeverCacheMixinTestCase(ViewTestMixin, TestCase):
    view_class = NeverCacheView
    
    def test_dispatch(self):
        response = self.run_view('get')
        procedural_response = never_cache_procedural('dummy')
        
        # headers should match
        self.assertItemsEqual(response.items(), procedural_response.items())
        self.assertEqual(response.content, 'hi')
        

class WorkingSingleObjectMixinTestCase(ViewTestMixin, TestCase):
    view_class = WorkingSingleObjectView
    
    def test_dispatch(self):
        with patch.object(self.view_class, 'get_object') as mock_get_object:
            mock_get_object.return_value = 'dummy'
            request = Mock()
            
            view = self.make_view('get', request_kwargs={ 'pk': 1, })
            view.dispatch(request)
            
            self.assertEqual(mock_get_object.call_count, 1)
            self.assertEqual(view.object, 'dummy')
        
        
class CategoryMixinTestCase(ViewTestMixin, TestCase):
    view_class = CategoryView
    
    def test__get_category(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='abcd')
        mixer.blend('notorhot.CandidateCategory')
        
        view = self.make_view('get', request_kwargs={ 'category_slug': 'abcd', })
        view_cat = view._get_category()
        self.assertEqual(view_cat, cat)
        
        view = self.make_view('get', request_kwargs={ 'slug': 'abcd', })
        view_cat = view._get_category(slug_name='slug')
        self.assertEqual(view_cat, cat)

        view = self.make_view('get', request_kwargs={ 'category_slug': 'def', })
        view_cat = view._get_category()
        self.assertIsNone(view_cat)
    
    def test_get_category(self):
        cat = mixer.blend('notorhot.CandidateCategory', slug='abcd')        
        view = self.make_view('get', request_kwargs={ 'category_slug': 'abcd', })
        with self.assertRaises(NotImplementedError):
            view_cat = view.get_category()

class ImplementedCategoryMixinTestCase(ViewTestMixin, TestCase):
    view_class = ImplementedCategoryView
    
    def test_category(self):
        view = self.make_view('get')

        view_cat = view.category
        self.assertEqual(view_cat, 'a category')
    
    
    def test_get_context_data(self):
        view = self.make_view('get')

        context = view.get_context_data()
        self.assertTrue('category' in context)
        self.assertEqual(context['category'], 'a category')
    
