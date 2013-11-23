from model_utils import FieldTracker


class AbstractFieldTracker(FieldTracker):
    def finalize_class(self, sender, name, **kwargs):
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super(AbstractFieldTracker, self).finalize_class(sender, **kwargs)

    
