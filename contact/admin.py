from django.contrib import admin
from contact import models

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'id', 'first_name', 'last_name', 'phone', 'category', 'show',
    ordering = '-id',
    list_filter = 'category', 'show', 'create_date',
    search_fields = 'id', 'first_name', 'last_name', 'phone', 'email',
    list_per_page = 15
    list_max_show_all = 100
    list_editable = 'first_name', 'last_name', 'category', 'show',
    list_display_links = 'id', 'phone',
    date_hierarchy = 'create_date'
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'picture')
        }),
        ('Contato', {
            'fields': ('phone', 'email')
        }),
        ('Detalhes', {
            'fields': ('description', 'category', 'show')
        }),
        ('Sistema', {
            'fields': ('owner', 'create_date'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('create_date',)

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name',
    ordering = 'name',
    search_fields = 'name',
    list_per_page = 20
