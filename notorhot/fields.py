from sorl.thumbnail import ImageField
from django.db.models.fields.files import FileDescriptor, ImageFileDescriptor


class AutoDocumentableFileDescriptorMixin(object):
    """
    Django FileFields (and by extension, Sorl ImageFields) cause 
    ``sphinx.ext.autodoc`` to throw AttributeErrors because their descriptors 
    raise AttributeErrors when accessed for model classes rather than instances.
    
    This can be mixed into a Django FileDescriptor or ImageFileDescriptor and 
    applied to any FileField subclass by subclassing the subclass and setting 
    the ``descriptor_class`` class attribute on the FileField subclass.
    
    See ``AutoDocumentableImageFileDescriptor`` and 
    ``AutoDocumentableImageField``, below, for examples.
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
    descriptor_class = AutoDocumentableFileDescriptor