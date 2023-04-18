from django.contrib import admin
from .models import SystemPortal, PlatformPortal, DataPortal

class SystemPortalAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["name", "more_details", "created_at"]
    list_display_links = ["name"]
    list_editable = ["more_details"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]

class PlatformPortalAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["name", "system", "sequence", "active", "more_details", "created_at"]
    list_display_links = ["name"]
    list_editable = ["sequence", "more_details", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active"]

class DataPortalAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["identifier", "platform", "more_details", "created_at"]
    list_display_links = ["identifier"]
    list_editable = ["more_details"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["identifier"]
    list_filter = ["platform"]

admin.site.register(SystemPortal, SystemPortalAdmin)
admin.site.register(PlatformPortal, PlatformPortalAdmin)
admin.site.register(DataPortal, DataPortalAdmin)
