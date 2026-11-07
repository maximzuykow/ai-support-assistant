from django.contrib import admin

from .models import KnowledgeArticle


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'source',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content', 'source')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('title',)