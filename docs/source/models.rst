**********************
django-notorhot Models
**********************

.. contents:: Table of Contents
   :local:
   :backlinks: top   

Candidate
---------

A candidate is whatever type of "thing" you want people to be able to vote on.  If you're comparing vegetables for popularity, then broccoli, peppers, celery, and green beans would each be candidates.  If you're comparing fruits, then apples, pears, oranges, kiwis, and dragon fruits would each be different candidates.

The ``Candidate`` model also stores information about its aggregate voting history: how many times it's been presented for a vote; how many times those competitions have been voted on (rather than reloaded or abandoned); and how many of those competitions it's won.  These fields are technically redundant, as they can be generated from the data in the Competition database table; but those calculations are awkward, expensive, and not straightforward to accomplish via Django's ORM; thus we record them separately.

``Candidate` also has a ``win_percentage`` property, which is calculated as ``wins / voted_competitions``.

``Candidate``'s managers use a custom ``QuerySet`` class that offers methods to filter and sort by common attributes, including the calculated win percentage property.  Because these are queryset rather than manager methods, they can be chained with one another and with normal queryset methods such as ``.filter()`` and ``.order_by``.

``.enabled()`` 
   Returns only Candidates having ``is_enabled == True``.

``.for_category(category)``
   Returns only Candidates belonging to the specified category.

``.order_by_wins()`` 
   Returns a queryset sorted by the calculated win percentage value in descending order (handy for use in leaderboards)

In addition to ``Candidate.objects``, there is a ``Candidate.enabled`` manager that returns only Candidates with ``is_enabled == True``.  This manager is used in all non-admin views bundled with django-not-or-hot.  Candidates can be taken out of circulation by setting their ``is_enabled`` attribute to ``False``.


Category
--------

django-notorhot provides for voting on multiple types of candidates on a single instance  of the app.  For instance, you might want to allow people to compare kittens to kittens and puppies to puppies, but not kittens to puppies.  Or you might want to be able to compare kittens to puppies and fruits to vegetables but not kittens to vegetables (or you might, you know -- the world's your oyster!)

In any case, each Candidate belongs to a Category and will only be offered in competitions against other Candidates in the same Category.  Similarly, leaderboards are segmented by category.

Each Category has a name, a slug, and a field to enable or disable public display.  In addition to ``Category.objects``, a ``Category.public`` manager is avaialble that returns only Categories with ``is_public == True``.  A Category with ``is_public == False`` will not be listed; its leaderboard will not be accessible; and users will not be able to see or vote on competitions for its candidates.  However, currently, Candidate details are still accessible via direct link for a Category that has been disabled (this may change in an upcoming release).

``Category`` has a method to generate a Competition between Candidates in the category, which in turn calls a method on the Competition manager (see below).

Competition
-----------

A Competition is a comparison between two Candidates in a category, one designated as the "left" Candidate and one as the "right" candidate.  When creating a Competition via a form (as in the admin), both Candidates must belong to the same Category, or an error will be thrown during validation.  When a Competition is creted or a vote is recorded on a Competition, the Competition will also update statistics for each of its Candidates.

Competition also has fields to record: 

* the date it was presented
* the date (if any) that a vote was recorded for the competition
* the winning candidate
* which side the winning candidate was on (technically redundant, but useful for statistical purposes)

``Competition``'s managers use a custom ``QuerySet`` class that offers a ``.votable()`` method to filter by whether the Competition has already been voted on.  Because this is a queryset rather than manager method, it can be chained with normal queryset methods such as ``.filter()`` and ``.order_by``.  

Competition's managers also include methods to generate new Competitions -- either selecting two Candidates at random from all enabled Candidates; selecting two Candidates from a provided QuerySet; or from two specific candidates.  Note that currently these manager methods are capable of producing Competition instances whose Candidates are from differing Categories.  This may be fixed in future releases. 

In addition to the standard manager, a ``Competition.votable`` manager is available that returns only Competitions that have not yet been voted on and that are thus still eligible to record new votes.




