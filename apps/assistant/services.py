from apps.assistant.providers import get_llm_provider
from apps.knowledge.services import search_knowledge
from apps.tickets.models import Ticket


def generate_draft(ticket: Ticket) -> str:
    articles = search_knowledge(
        f'{ticket.subject} {ticket.message}',
    )

    knowledge_context = '\n\n'.join(
        f'Title: {article.title}\nContent: {article.content}'
        for article in articles
    )

    if not knowledge_context:
        knowledge_context = 'No relevant knowledge articles found.'

    prompt = f"""
You are a customer support assistant.

Use the knowledge base to answer the customer's question.
Do not invent information.
If the knowledge base does not contain enough information,
say that the request requires review by a human operator.

Knowledge base:
{knowledge_context}

Customer:
{ticket.customer_name}

Subject:
{ticket.subject}

Message:
{ticket.message}

Write a clear, polite and helpful response.
"""

    provider = get_llm_provider()
    return provider.generate(prompt)