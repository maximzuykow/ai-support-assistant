from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from .models import KnowledgeArticle


def search_knowledge(query: str, limit: int = 5) -> list[KnowledgeArticle]:
    search_query = SearchQuery(query, config='english')

    return list(
        KnowledgeArticle.objects
        .filter(is_active=True)
        .annotate(
            search=SearchVector(
                'title',
                weight='A',
                config='english',
            ) + SearchVector(
                'content',
                weight='B',
                config='english',
            ),
        )
        .filter(search=search_query)
        .annotate(rank=SearchRank('search', search_query))
        .order_by('-rank')[:limit]
    )