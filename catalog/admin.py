from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ORF, Accession, Family, Group, ISElement, Origin, Synonym

# ==========================================
# 1. INLINES (For 1-to-Many Relationships)
# ==========================================


class ISElementInlineForOrigin(admin.TabularInline):
    model = ISElement
    fields = ("name", "family", "group", "length")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ISElementInlineForFamily(admin.TabularInline):
    model = ISElement
    fields = ("name", "length", "group", "origin")  # Requested columns
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ISElementInlineForGroup(admin.TabularInline):
    model = ISElement
    fields = ("name", "family", "length", "origin")  # Requested columns
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ISElementInlineForAccession(admin.TabularInline):
    model = ISElement
    # "All the information" requested
    fields = ("name", "family", "group", "length", "origin", "number")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ==========================================
# 2. MODEL ADMINS (Attaching the Inlines)
# ==========================================


class ISElementAdmin(SimpleHistoryAdmin):
    # Search by the element's name OR the origin's name
    search_fields = ["name", "origin__name"]
    # this changes the main list view to show the columns
    list_display = ("name", "origin", "family", "group", "length")


class OriginAdmin(SimpleHistoryAdmin):
    search_fields = ["name"]  #this adds the search bar
    inlines = [ISElementInlineForOrigin]


class AccessionAdmin(SimpleHistoryAdmin):
    search_fields = ["accession"]
    inlines = [ISElementInlineForAccession]


class FamilyAdmin(SimpleHistoryAdmin):
    search_fields = ["name"]
    inlines = [ISElementInlineForFamily]


class GroupAdmin(SimpleHistoryAdmin):
    search_fields = ["name"]
    inlines = [ISElementInlineForGroup]


# ==========================================
# 3. SYNONYM ADMIN (Pulling Parent Data)
# ==========================================


class SynonymAdmin(SimpleHistoryAdmin):
    # fields will show at the bottom of the Synonym edit page
    search_fields = ["name"]
    readonly_fields = (
        "real_is_name",
        "associated_family",
        "associated_group",
        "associated_origin",
        "associated_length",
    )

    def get_parent(self, obj):
        """Helper to find the parent IS Element regardless of what you named the ForeignKey in models.py"""
        if hasattr(obj, "iselement"):
            return obj.iselement
        if hasattr(obj, "is_element"):
            return obj.is_element
        return None

    def real_is_name(self, obj):
        parent = self.get_parent(obj)
        return parent.name if parent else "None"

    real_is_name.short_description = "Real Name (IS Element)"

    def associated_family(self, obj):
        parent = self.get_parent(obj)
        return parent.family.name if parent and parent.family else "None"

    associated_family.short_description = "Family"

    def associated_group(self, obj):
        parent = self.get_parent(obj)
        return parent.group.name if parent and parent.group else "None"

    associated_group.short_description = "Group"

    def associated_origin(self, obj):
        parent = self.get_parent(obj)
        return parent.origin.name if parent and parent.origin else "None"

    associated_origin.short_description = "Origin"

    def associated_length(self, obj):
        parent = self.get_parent(obj)
        return parent.length if parent else "None"

    associated_length.short_description = "Length"


# ==========================================
# 4. REGISTRATION
# ==========================================

# Register the models with their new custom admin layouts
admin.site.register(Origin, OriginAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Accession, AccessionAdmin)
admin.site.register(Synonym, SynonymAdmin)

# Register the standalone models normally
admin.site.register(ISElement)
admin.site.register(ORF)
