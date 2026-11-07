from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q

from .models import KnowledgeArticle


def search_knowledge(query: str, limit: int = 5) -> list[KnowledgeArticle]:
    search_query = SearchQuery(query, config='simple')

    search_vector = (
        SearchVector('title', weight='A', config='simple')
        + SearchVector('content', weight='B', config='simple')
    )

    articles = list(
        KnowledgeArticle.objects
        .filter(is_active=True)
        .annotate(search=search_vector)
        .filter(search=search_query)
        .annotate(rank=SearchRank('search', search_query))
        .order_by('-rank')[:limit]
    )

    if articles:
        return articles

    words = [
        word.lower().strip(".,!?;:()[]{}\"'")
        for word in query.split()
        if len(word.strip(".,!?;:()[]{}\"'")) >= 3
    ]

    filters = Q()

    for word in words:
        filters |= Q(title__icontains=word[:7])
        filters |= Q(content__icontains=word[:7])

    if not words:
        return []

    return list(
        KnowledgeArticle.objects
        .filter(is_active=True)
        .filter(filters)
        .distinct()[:limit]
    )