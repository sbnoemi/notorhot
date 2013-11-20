from notorhot._tests.models import NotorHotCategoryTestCase, \
    NotorHotCandidateTestCase, NotorHotCompetitionTestCase
    
from notorhot._tests.forms import NotorHotVoteFormTestCase

from notorhot._tests.views import CompetitionViewTestCase, VoteViewTestCase, \
    CandidateViewTestCase, LeaderboardViewTestCase, CategoryListViewTestCase

from notorhot._tests.utils import NeverCacheMixinTestCase, \
    WorkingSingleObjectMixinTestCase, CategoryMixinTestCase, \
    ImplementedCategoryMixinTestCase

# need non-overlapping names
from notorhot._tests.integration import CompetitionViewTestCase as CompTestCast, \
    VoteViewTestCase as VoteTestCase, CandidateViewTestCase as CandTestCase, \
    LeaderboardViewTestCase as LeadTestCase, \
    CategoryListViewTestCase as CatTestCase, AbsoluteURLTestCase

