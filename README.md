# AI Support Assistant

AI-powered customer support automation system built with Django, Django REST Framework, Celery, Redis and PostgreSQL.

The system receives support tickets through webhooks, processes them asynchronously, searches a knowledge base, generates AI response drafts and allows operators to review, approve or reject responses before sending them to an external helpdesk.

## Features

- REST API for incoming support webhooks
- Webhook event deduplication
- Asynchronous background processing with Celery
- Transactional Outbox pattern
- OpenAI integration for AI response generation
- Static fallback response when no LLM API key is configured
- Knowledge base with PostgreSQL full-text search
- Global rate limiting using Redis (60 requests per minute)
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
6. The LLM provider generates a response draft using the knowledge base context.
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

### 5. Start PostgreSQL and Redis

PostgreSQL and Redis must be running before starting the application.

Configure their connection details in `.env`.

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create administrator

```bash
python manage.py createsuperuser
```

### 8. Start Django

```bash
python manage.py runserver
```

Django will be available at:

`http://127.0.0.1:8000/`

### 9. Start Celery Worker

Open a separate terminal:

```powershell
python -m celery -A config worker -l info --pool=solo
```

### 10. Start Celery Beat

Open another terminal:

```powershell
python -m celery -A config beat -l info
```

Celery Beat dispatches pending Outbox events every 5 seconds.

### 11. Start Mock Helpdesk

Open another terminal:

```powershell
python manage.py runserver 8001
```

Mock Helpdesk will be available at:

`http://127.0.0.1:8001/`

## Main Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/webhooks/helpdesk` | Receive support ticket webhook |
| GET | `/api/tickets/` | List tickets |
| GET | `/api/tickets/<id>/` | Retrieve ticket |
| POST | `/api/drafts/<id>/approve/` | Approve draft |
| POST | `/api/drafts/<id>/reject/` | Reject draft |
| GET | `/api/operator/` | Operator dashboard |
| GET | `/health` | Health check |

## Knowledge Base

The project includes a knowledge base with short articles for a fictional product called CloudDesk.

Articles are stored in PostgreSQL and searched using PostgreSQL full-text search with an additional fallback search.

The retrieved articles are included in the prompt sent to the LLM provider.

## LLM Configuration

Configure the provider using environment variables:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

When an API key is configured, the application sends requests to OpenAI.

When no API key is configured, the application still makes a real HTTP request to the provider, waits for a simulated processing delay and returns a static fallback response.

The fallback allows the rest of the ticket-processing and operator-approval workflow to be demonstrated without a paid API key.

## Environment Variables

See `.env.example` for the required configuration.

Important variables:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_URL`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `HELPDESK_API_KEY`

## Security

- Environment secrets are stored outside the repository.
- `.env` is excluded from Git.
- Operator views require staff authentication.
- Mock Helpdesk requests require API key authentication.
- Webhook events support deduplication.
- Outgoing replies use idempotency keys to prevent duplicate responses.

## Testing

The application includes a GitHub Actions workflow that checks the Django configuration, validates migrations and runs database migrations.

## Project Status

This project was developed as a backend engineering take-home assignment.

