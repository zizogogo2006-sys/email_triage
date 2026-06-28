# Email Triage

Triages and drafts responses to customer support emails via IMAP and OpenAI.

## Architecture
- Language: Python 3.11+
- Integrations: IMAP (Gmail)
- LLM: OpenAI GPT-4o

## Setup

Run locally with Docker:
```bash
docker-compose up --build
```

Run tests:
```bash
pytest tests/
```
