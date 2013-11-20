from copy import copy

from django.test import RequestFactory
from notorhot._tests.factories import mixer

# courtesy of http://tech.novapost.fr/django-unit-test-your-views-en.html
def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.
    args and kwargs are the same you would pass to ``reverse()``
    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view
    

class ViewTestMixin(object):
    view_class = None
    
    def make_request(self, method, data, session_data):
        if method == 'post':
            request = RequestFactory().post('/path/unimportant/', data=data)
        else:
            request = RequestFactory().get('/path/unimportant/', data=data)
            
        if session_data is not None:
            request.session = copy(session_data)
            
        return request
        
    
    def make_view(self, method, data={}, view_args=(), view_kwargs={}, 
            request_args=(), request_kwargs={}, session_data=None):

        request = self.make_request(method, data, session_data)
        view = self.view_class(*view_args, **view_kwargs)

        return setup_view(view, request, *request_args, **request_kwargs)

    def run_view(self, method, data={}, view_args=(), view_kwargs={}, 
            request_args=(), request_kwargs={}, session_data=None):
            
        request = self.make_request(method, data, session_data)        
        view = self.view_class.as_view(*view_args, **view_kwargs)

        return view(request, *request_args, **request_kwargs)
        
        
def generate_leaderboard_data(cat1, cat2):
    cand1 = mixer.blend('notorhot.Candidate', votes=18, wins=9, category=cat1, is_enabled=True) # .5
    cand2 = mixer.blend('notorhot.Candidate', votes=15, wins=8, category=cat1, is_enabled=True) # .5333
    cand3 = mixer.blend('notorhot.Candidate', votes=12, wins=7, category=cat1, is_enabled=True) # .58333
    cand4 = mixer.blend('notorhot.Candidate', votes=9, wins=6, category=cat1, is_enabled=True) # .6667
    
    mixer.blend('notorhot.Candidate', votes=18, wins=17, category=cat2) 
    mixer.blend('notorhot.Candidate', votes=15, wins=14, category=cat2) 
    mixer.blend('notorhot.Candidate', votes=12, wins=11, category=cat2) 
    mixer.blend('notorhot.Candidate', votes=9, wins=8, category=cat2) 
    
    mixer.blend('notorhot.Candidate', votes=18, wins=17, category=cat1, is_enabled=False) 
    mixer.blend('notorhot.Candidate', votes=15, wins=14, category=cat1, is_enabled=False) 
    mixer.blend('notorhot.Candidate', votes=12, wins=11, category=cat1, is_enabled=False) 
    mixer.blend('notorhot.Candidate', votes=9, wins=8, category=cat1, is_enabled=False) 

    return (cand1, cand2, cand3, cand4)