from sorl.thumbnail import ImageField
from django.db.models.fields.files import FileDescriptor, ImageFileDescriptor


class AutoDocumentableFileDescriptorMixin(object):
    """
    Django :class:`FileField` (and by extension,  Sorl :class:`ImageField`) cause 
    :mod:`sphinx.ext.autodoc` to throw an :exc:`AttributeError` because 
    their descriptors raise :exc:`AttributeError` when accessed for model 
    classes rather than instances.
    
    This can be mixed into a Django :class:`FileDescriptor` or 
    :class:`ImageFileDescriptor` and applied to any :class:`FileField` subclass 
    by subclassing the subclass and setting the :attr:`descriptor_class` class 
    attribute on the :class:`FileField` subclass.
    
    See source of :class:`AutoDocumentableImageFileDescriptor` and 
    :class:`AutoDocumentableImageField` for examples.
    """
    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
            
        return super(AutoDocumentableFileDescriptorMixin, self).__get__(
            instance=instance, owner=owner)
        
        
class AutoDocumentableFileDescriptor(AutoDocumentableFileDescriptorMixin, 
        FileDescriptor):
    pass
        
class AutoDocumentableImageFileDescriptor(AutoDocumentableFileDescriptorMixin, 
        ImageFileDescriptor):
    pass

        
class AutoDocumentableImageField(ImageField):
    """
    Sorl Thumbnail :class:`ImageField` subclass that is Sphinx Autodoc-friendly.
    """
    descriptor_class = AutoDocumentableFileDescriptor