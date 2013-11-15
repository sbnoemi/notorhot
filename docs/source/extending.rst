*************************
Extending django-notorhot
*************************

.. contents:: Table of Contents
   :local:
   :backlinks: top   

Custom Templates
----------------

If you want to change what data is output to the templates, what CSS hooks are available, or the block names / base templates used to extend the templates, you can create a template in your app with the same filename, as explained in the `Django tutorial <https://docs.djangoproject.com/en/1.6/intro/tutorial02/#customizing-your-project-s-templates>`_.


Additional Model Data
---------------------

To display additional data about a candidate, you'll need to create a model with a relationship to Candidate (don't forget to set the ``related_name``!), and override a template to output that data.  For example, suppose you had an app called ``myapp`` and wanted to display nutritional information and links to recipes for your fruits and vegetables:

.. code-block:: python

   # myapp/models.py
   
   from django.db import models
   from notorhot.models import Candidate
   
   class NutritionData(models.Model):
      candidate = models.OneToOneField(Candidate, related_name=nutrition)
      calories = models.PositiveIntegerField()
      
   
   class RecipeLinks(models.Model):
      candidate = models.ForeignKey(Candidate, related_name=recipes)
      title = models.CharField(max_length=100)
      url = models.URLField()
      
      def __unicode__(self):
         return self.title
         
.. code-block:: html

    <!-- myapp/templates/notorhot/candidate_main.html -->
   
    {% load thumbnail %}

    <h1>{{ candidate.name }}</h1>
    {% if candidate.nutrition %}
        <p class="nutrition">{{ candidate.nutrition.calories }} calories per serving</p>
    {% endif %}
    
    {% include 'notorhot/new_competition.html' %}
    
    <div id="candidate_data">        
        {% thumbnail candidate.pic "300x600" as thumb %}
            <img src="{{ thumb.url }}" alt="{{ candidate.name }}" />
        {% endthumbnail %}

        <h2>Recipes using {{ candidate.name }}</h2>
        {% if candidate.recipes.count %}
            <ul>
                {% for recipe in candidate.recipes.all %}
                    <li>
                        <a href="{{ recipe.url }}">{{ recipe.title }}</a>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No recipes found for {{ candidate.name }}</p>
        {% endif %}
            
    </div><!-- /candidate_data -->


View Overrides
--------------

To change behavior, you will have to override django-notorhot's views.  The views are designed as class-based views so as to permit overrides of view behavior by subclassing, with minimal duplication of logic.

For instance, suppose that after a vote, you wanted to display the winning Candidate's detail page instead of offering the user a new Competition.  To do that, you would have to first subclass ``VoteView`` and override its ``get_success_url()`` method; and second, hook up the voting URL to your ``VoteView`` subclass:

.. code-block:: python

   # myapp/views.py
   
   from notorhot.views import VoteView
   
   class MyVoteView(VoteView):      
  
       def get_success_url(self):
           return self.object.winner.get_absolute_url()
   
   
.. code-block:: python

   # myproject/urls.py
   
   from myapp.views import MyVoteView
   
   urlpatterns = patterns('',
      ...
      url(r'any-custom-path/vote/(?P<pk>\d+)/$', MyVoteView.as_view(), name='notorhot_vote'),
      url(r'any-custom-path/', include('notorhot.urls')),
      ...
   )