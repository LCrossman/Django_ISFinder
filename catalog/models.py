from django.db import models
from simple_history.models import HistoricalRecords 
 
class Family(models.Model):
    """
    Top-level IS classification.
    e.g. IS1, IS3, IS4
    One Family has many Groups and many ISElements.
    """
    name = models.CharField(max_length=50, unique=True)
    history = HistoricalRecords()
    class Meta:
        verbose_name_plural = 'Families'
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
 
class Group(models.Model):
    """
    Sub-classification within a Family.
    e.g. ISAs1 belongs to a Family.
    Often empty/NA on ISElements — nullable FK.
    """
    name   = models.CharField(max_length=50, unique=True)
    family = models.ForeignKey(Family, on_delete=models.PROTECT, related_name='groups')
    history = HistoricalRecords()
    class Meta:
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
 
class Origin(models.Model):
    """
    Host organism / strain the IS element was found in.
    e.g. Acaryochloris marina
    Reused across many ISElements.
    """
    name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()
    class Meta:
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
 
class Accession(models.Model):
    """
    GenBank accession number.
    One accession can be associated with many ISElements.
    e.g. NC_009925
    """
    number = models.CharField(max_length=20, unique=True, db_index=True)
    history = HistoricalRecords()
    class Meta:
        ordering = ['number']
 
    def __str__(self):
        return self.number
 
 
class ISElement(models.Model):
    """
    Core IS element entry — one row in the ISFinder dataset.
    """
    number    = models.IntegerField(null=True, blank=True)       # N° — e.g. 7
    name      = models.CharField(max_length=50, unique=True,
                                 db_index=True)                        # e.g. ISAcma2
    family    = models.ForeignKey(Family, on_delete=models.PROTECT,
                                  related_name='elements')
    group     = models.ForeignKey(Group, on_delete=models.PROTECT,
                                  related_name='elements',
                                  null=True, blank=True)               # NA → null
    origin    = models.ForeignKey(Origin, on_delete=models.PROTECT,
                                  related_name='elements')
    accession = models.ForeignKey(Accession, on_delete=models.PROTECT,
                                  related_name='elements')
    iso       = models.CharField(max_length=100, blank=True)           # isolation info
    length    = models.IntegerField(null=True, blank=True)                                  # total length in bp
    ir_min    = models.IntegerField(null=True, blank=True)                                  # Inverted Repeat — single value or min of range
    ir_max    = models.IntegerField(null=True, blank=True)             # null when single value, e.g. 18; set when range e.g. 17/18
    dr        = models.IntegerField(null=True, blank=True)                                  # Direct Repeat length
    url       = models.URLField(max_length=200)
    history = HistoricalRecords()
    class Meta:
        ordering = ['number']
 
    def __str__(self):
        return self.name
 
 
class Synonym(models.Model):
    """
    Alternative names for an ISElement.
    Separate model so synonyms are individually searchable/indexable.
    """
    name       = models.CharField(max_length=30, db_index=True)
    history = HistoricalRecords()
    is_element = models.ForeignKey(ISElement, on_delete=models.CASCADE,
                                   related_name='synonyms')
 
    class Meta:
        ordering = ['name']
        unique_together = ('name', 'is_element')
 
    def __str__(self):
        return f"{self.name} → {self.is_element.name}"
 
 
class ORF(models.Model):
    """
    Open Reading Frame within an ISElement.
    One ISElement can have multiple ORFs — e.g. '122 (84-452)146 (404-844)'.
    aa_length is indexed for filtering; coordinates stored for display only.
    """
    is_element = models.ForeignKey(ISElement, on_delete=models.CASCADE,
                                   related_name='orfs')
    aa_length  = models.IntegerField(db_index=True,null=True, blank=True)   # amino acid count — e.g. 496
    start      = models.IntegerField(null=True, blank=True)                # start coordinate — e.g. 7293
    end        = models.IntegerField(null=True, blank=True)                # end coordinate   — e.g. 582 (can be < start on circular genomes)
    history = HistoricalRecords()
    class Meta:
        ordering = ['aa_length']
 
    def __str__(self):
        return f"{self.is_element.name} ORF {self.aa_length}aa ({self.start}-{self.end})"
