from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import Family, Origin, Accession, ISElement

class ISElementModelTests(TestCase):
    
    def setUp(self):
        #setUp runs before every test to build a fake test data
        self.family = Family.objects.create(name="IS3")
        self.origin = Origin.objects.create(name="E. coli")
        self.accession = Accession.objects.create(number="NC_000913")
        
        self.element = ISElement.objects.create(
            name="IS150",
            family=self.family,
            origin=self.origin,
            accession=self.accession,
            length=1443
        )

    def test_element_creation_and_relationships(self):
        #check the element was saved and linked properly
        self.assertEqual(self.element.name, "IS150")
        self.assertEqual(self.element.family.name, "IS3")
        self.assertEqual(self.element.length, 1443)

    def test_string_representation(self):
        #check that __str__ returns the name
        self.assertEqual(str(self.element), "IS150")

    def test_simple_history_tracking(self):
        #check that the initial creation was logged
        self.assertEqual(self.origin.history.count(), 1)
        
        #make an edit and save it
        self.origin.name = "Escherichia coli"
        self.origin.save()
        
        #check that the time-machine caught the edit
        self.assertEqual(self.origin.history.count(), 2)
        
        #verify the old version is preserved
        old_version = self.origin.history.last()
        self.assertEqual(old_version.name, "E. coli")
