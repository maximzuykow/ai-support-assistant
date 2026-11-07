# AI Support Assistant

AI-powered customer support automation system built with Django, Django REST Framework, Celery, Redis and PostgreSQL.

The system receives support tickets through webhooks, processes them asynchronously, searches a knowledge base, generates AI response drafts and allows operators to review, approve or reject responses before sending them to an external helpdesk.

## Features

- REST API for incoming support webhooks
- Webhook event deduplication
- Asynchronous background processing with Celery
- Transactional Outbox pattern
- AI response generation with OpenAI integration
- Mock LLM provider for local development
- Knowledge base with PostgreSQL full-text search
- Global rate limiting using Redis
- Operator dashboard for reviewing AI-generated drafts
- Approve and reject workflow
- Mock Helpdesk integration
- Idempotent response delivery
- PostgreSQL database

## Architecture

1. External helpdesk sends a ticket webhook.
2. Django validates and stores the event.
3. An Outbox event is created in the same database transaction.
4. Celery Beat dispatches pending events to Celery Worker.
5. The worker creates a ticket and searches the knowledge base.
6. The LLM generates a response draft.
7. An operator reviews the draft in the dashboard.
8. Approved drafts are sent to the helpdesk.
9. The draft status changes to `sent`.

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- OpenAI API
- HTTPX
- GitHub Actions

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/maximzuykow/ai-support-assistant.git
cd ai-support-assistant
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure your local settings.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create administrator

```bash
python manage.py createsuperuser
```

### 7. Start Django

```bash
python manage.py runserver
```

### 8. Start Celery Worker

```bash
python -m celery -A config worker -l info --pool=solo
```

### 9. Start Celery Beat

```bash
python -m celery -A config beat -l info
```

Redis and PostgreSQL must be running before starting the application.

## Main Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/webhooks/` | Receive support ticket webhook |
| GET | `/api/tickets/` | List tickets |
| GET | `/api/tickets/<id>/` | Retrieve ticket |
| POST | `/api/drafts/<id>/approve/` | Approve draft |
| POST | `/api/drafts/<id>/reject/` | Reject draft |
| GET | `/api/operator/` | Operator dashboard |

## Environment Variables

See `.env.example` for the required configuration.

## Security

- Environment secrets are stored outside the repository.
- `.env` is excluded from Git.
- Operator views require staff authentication.
- Mock Helpdesk requests require API key authentication.
- Webhook events and outgoing replies support idempotency.

## Project Status

This project is under active development.