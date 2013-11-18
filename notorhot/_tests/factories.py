from copy import copy

from mixer.backend.django import Mixer, GenFactory
from mixer import generators as g, fakers as f
from autoslug import AutoSlugField

gen_generators = copy(GenFactory.generators)
if AutoSlugField not in gen_generators:
    gen_generators.update({
        AutoSlugField: g.gen_string,
    })

class AutoSlugFactory(GenFactory):
    generators = gen_generators

mixer = Mixer(factory=AutoSlugFactory)