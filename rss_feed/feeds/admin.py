from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Feed, Item


class ItemInlineAdmin(admin.StackedInline):
    model = Item
    fields = ('created', 'last_update', 'title', 'link', 'published_time')
    readonly_fields = fields
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_update', 'created_by', 'title', 'is_auto_update',
                       'link', 'description', 'image', 'is_followed', '_items_count')
    fieldsets = (
        (None, {'fields': ('title', 'xml_url')}),
        (_('More Info'), {'fields': (
            ('link', 'created_by', 'image'),
            ('is_followed', 'is_auto_update'),
            'description', '_items_count')}),
        (_('Important dates'), {'fields': ('created', 'last_update',)}),
    )
    list_display = ('title', 'xml_url', 'is_auto_update',)
    inlines = [ItemInlineAdmin]

    def _items_count(self, obj):
        return obj.items.count()
    _items_count.short_description = 'Items Count'
