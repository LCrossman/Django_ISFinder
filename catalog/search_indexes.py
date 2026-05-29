from haystack import indexes
from .models import ISElement

class ISElementIndex(indexes.SearchIndex, indexes.Indexable):
    #The primary searchable Document
    text = indexes.CharField(document=True, use_template=True)
    
    #Filtering Fields 
    #allow users to do faceted searches (e.g., "Show me matches, but only from Family IS3")
    name = indexes.CharField(model_attr='name')
    family = indexes.CharField(model_attr='family__name')
    group = indexes.CharField(model_attr='group__name', null=True)
    origin = indexes.CharField(model_attr='origin__name')
    accession = indexes.CharField(model_attr='accession__number')
    
    #Adding numeric fields if you want to allow range sliders in your UI later
    # (e.g., "Find elements with length > 1500bp")
    length = indexes.IntegerField(model_attr='length', null=True)

    def get_model(self):
        return ISElement

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        #using select_related and prefetch_related prevents the "N+1 query problem"
        #Django grabs all related data in one massive query instead of 
        #doing thousands of tiny queries while building the index.
        return self.get_model().objects.select_related(
            'family', 'group', 'origin', 'accession'
        ).prefetch_related('synonyms', 'orfs')
