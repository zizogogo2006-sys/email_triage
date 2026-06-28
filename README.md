# AI Support Email Triage

Enterprise-grade microservice for automatically triaging and drafting responses to customer support emails using IMAP and OpenAI.

## Architecture
- **Language**: Python 3.11+
- **Integrations**: IMAP (Gmail)
- **LLM**: OpenAI GPT-4o

## Infrastructure
This service is fully containerized and includes a CI/CD pipeline.

### Running Locally with Docker
```bash
docker-compose up --build
```

### Running Tests
We use Pytest for continuous integration.
```bash
pytest tests/
```
