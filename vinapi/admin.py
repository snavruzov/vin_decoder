"""
Admin interface to handle CRUD operations
There is defined jsoneditor package to manage JSON specified fields in Postgresql database
"""
from django.contrib import admin

from vinapi.models import Basic


class BasicAdmin(admin.ModelAdmin):
    readonly_fields = ('VIN',)
    search_fields = ['VIN']

    fieldsets = [
        ('Basic Details', {'fields': ['VIN', 'year', 'make', 'model', 'type', 'color']}),
        (None, {'fields': ('dimensions', 'weight')}),
    ]

    list_display = ('VIN', 'make', 'model', 'year')


admin.site.register(Basic, BasicAdmin)

